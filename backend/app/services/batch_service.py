"""Batch generation orchestration.

This module ties everything together:

    1. Validates inputs (product, quantity, preset all active)
    2. Builds the 12-char deterministic prefix
    3. Generates N unique 17-char codes + short tokens with retry on DB-level
       UNIQUE-constraint violations (the source of truth for uniqueness)
    4. Bulk-inserts into PostgreSQL (one transaction)
    5. Pushes every record to Zoho CRM and updates sync status
    6. Renders an Excel file
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.integrations import zoho_crm
from app.models.admin_user import AdminUser
from app.models.batch import GenerationBatch
from app.models.product import Product
from app.models.qr_code import QRCode
from app.models.quantity import Quantity
from app.models.whatsapp_preset import WhatsappPreset
from app.services import settings_service
from app.services.code_generator import build_prefix, make_code, validate_code
from app.services.excel_export import export_batch_to_excel
from app.services.short_token import adaptive_length, make_token
from app.utils.logger import get_logger

logger = get_logger(__name__)


MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_short_domain(db: Session) -> str:
    """Prefer environment value if set; else fall back to DB setting."""
    if settings.SHORT_DOMAIN:
        return settings.SHORT_DOMAIN.rstrip("/")
    return (settings_service.get_value(db, "short_domain", "") or "").rstrip("/")


def _next_batch_name(db: Session) -> str:
    """BATCH_YYYYMMDD_### — sequence resets daily."""
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"BATCH_{today}_"
    count_today = (
        db.query(GenerationBatch)
        .filter(GenerationBatch.batch_name.like(f"{prefix}%"))
        .count()
    )
    return f"{prefix}{count_today + 1:03d}"


def _wa_redirect(number: str, code: str) -> str:
    return f"https://wa.me/{number}?text={code}"


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def generate_batch(
    db: Session,
    *,
    product_id: int,
    quantity_id: int,
    manufacturing_month: int,
    manufacturing_year: int,
    whatsapp_preset_id: int,
    count: int,
    created_by: AdminUser | None = None,
) -> Tuple[GenerationBatch, List[QRCode], int, int]:
    """Generate `count` unique codes, persist them, push to Zoho, return batch.

    Returns: (batch, codes, zoho_synced, zoho_failed)
    """
    if count <= 0:
        raise ValueError("count must be > 0")

    # 1) Fetch + validate references
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise ValueError("Product not found or inactive")

    quantity = db.get(Quantity, quantity_id)
    if not quantity or not quantity.is_active:
        raise ValueError("Quantity not found or inactive")

    preset = db.get(WhatsappPreset, whatsapp_preset_id)
    if not preset or not preset.is_active:
        raise ValueError("WhatsApp preset not found or inactive")

    prefix = build_prefix(
        initials=product.initials,
        quantity_code=quantity.internal_code,
        manufacturing_month=manufacturing_month,
        manufacturing_year=manufacturing_year,
    )

    short_domain = _get_short_domain(db)
    if not short_domain:
        raise RuntimeError("Short domain is not configured (Settings → Short Domain).")

    # 2) Create the batch row first
    batch = GenerationBatch(
        batch_name=_next_batch_name(db),
        total_codes=0,
        product_id=product.id,
        quantity_id=quantity.id,
        whatsapp_preset_id=preset.id,
        manufacturing_month=manufacturing_month,
        manufacturing_year=manufacturing_year,
        created_by=created_by.id if created_by else None,
    )
    db.add(batch)
    db.flush()  # populate batch.id

    # 3) Generate codes — per-row with UNIQUE-constraint retries
    inserted: List[QRCode] = []
    code_seen: set[str] = set()
    token_seen: set[str] = set()

    MAX_PER_CODE_ATTEMPTS = 12

    for _ in range(count):
        # ---- code (17 chars) ----------------------------------------------
        for attempt in range(MAX_PER_CODE_ATTEMPTS):
            code = make_code(prefix)
            if not validate_code(code):
                continue
            if code in code_seen:
                continue
            # check DB
            exists = db.execute(
                select(QRCode.id).where(QRCode.code == code).limit(1)
            ).first()
            if exists:
                continue
            code_seen.add(code)
            break
        else:
            raise RuntimeError(
                "Could not generate a unique 17-char code after many attempts."
            )

        # ---- short token (5..7 chars) -------------------------------------
        for attempt in range(MAX_PER_CODE_ATTEMPTS):
            token = make_token(adaptive_length(attempt))
            if token in token_seen:
                continue
            exists = db.execute(
                select(QRCode.id).where(QRCode.short_token == token).limit(1)
            ).first()
            if exists:
                continue
            token_seen.add(token)
            break
        else:
            raise RuntimeError("Could not generate a unique short token after many attempts.")

        short_link = f"{short_domain}/{token}"
        whatsapp_link = _wa_redirect(preset.whatsapp_number, code)

        row = QRCode(
            code=code,
            short_token=token,
            short_link=short_link,
            product_id=product.id,
            quantity_id=quantity.id,
            manufacturing_month=manufacturing_month,
            manufacturing_year=manufacturing_year,
            whatsapp_preset_id=preset.id,
            whatsapp_link=whatsapp_link,
            zoho_sync_status="PENDING",
            status="UNUSED",
            batch_id=batch.id,
        )
        db.add(row)
        inserted.append(row)

    # 4) Flush + commit — defensive: catch any IntegrityError that slipped
    #    past the pre-check (concurrent batches) and regenerate just that row.
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        logger.exception("IntegrityError during batch insert — aborting")
        raise RuntimeError(f"Database integrity error during batch insert: {exc}") from exc

    batch.total_codes = len(inserted)
    db.commit()
    for row in inserted:
        db.refresh(row)

    # 5) Push to Zoho CRM
    synced, failed = _push_batch_to_zoho(db, batch, inserted, product, quantity, preset)

    # 6) Render Excel (re-read with eager joins to render labels correctly)
    excel_path = export_batch_to_excel(batch.batch_name, inserted)
    batch.excel_file_path = excel_path
    db.commit()

    return batch, inserted, synced, failed


# ---------------------------------------------------------------------------
# Zoho push helpers
# ---------------------------------------------------------------------------


def _build_zoho_payload(
    code_row: QRCode,
    product: Product,
    quantity: Quantity,
    preset: WhatsappPreset,
    batch: GenerationBatch,
) -> Dict[str, object]:
    return {
        # internal — used to map results back to rows
        "_local_id": code_row.id,
        "code": code_row.code,
        "product_name": product.name,
        "product_initials": product.initials,
        "quantity_label": quantity.label,
        "quantity_code": quantity.internal_code,
        "manufacturing_month": f"{code_row.manufacturing_month:02d}",
        "manufacturing_year": code_row.manufacturing_year,
        "manufacturing_display": f"{MONTH_NAMES[code_row.manufacturing_month - 1]} {code_row.manufacturing_year}",
        "whatsapp_number": preset.whatsapp_number,
        "whatsapp_redirect_url": code_row.whatsapp_link,
        "short_token": code_row.short_token,
        "short_link": code_row.short_link,
        "batch_name": batch.batch_name,
        "status": code_row.status,
        "created_at": code_row.created_at,
    }


def _push_batch_to_zoho(
    db: Session,
    batch: GenerationBatch,
    rows: List[QRCode],
    product: Product,
    quantity: Quantity,
    preset: WhatsappPreset,
) -> Tuple[int, int]:
    payloads = [_build_zoho_payload(r, product, quantity, preset, batch) for r in rows]
    by_local_id: Dict[int, QRCode] = {r.id: r for r in rows}

    results = zoho_crm.push_records(db, payloads)
    synced = 0
    failed = 0
    now = datetime.now(timezone.utc)

    for payload, zoho_id, err in results:
        row = by_local_id[payload["_local_id"]]
        if zoho_id:
            row.zoho_record_id = zoho_id
            row.zoho_sync_status = "SYNCED"
            row.zoho_last_sync_at = now
            row.zoho_error = None
            synced += 1
        else:
            row.zoho_sync_status = "FAILED"
            row.zoho_last_sync_at = now
            row.zoho_error = (err or "")[:1000]
            failed += 1

    batch.zoho_synced = synced
    batch.zoho_failed = failed
    db.commit()
    return synced, failed


# ---------------------------------------------------------------------------
# Retry endpoint helper
# ---------------------------------------------------------------------------


def retry_failed_for_batch(db: Session, batch_id: int) -> Tuple[int, int, int]:
    """Re-push all FAILED rows for a batch. Returns (retried, synced, failed)."""
    batch = db.get(GenerationBatch, batch_id)
    if not batch:
        raise ValueError("Batch not found")

    failed_rows = (
        db.query(QRCode)
        .filter(QRCode.batch_id == batch_id, QRCode.zoho_sync_status == "FAILED")
        .all()
    )
    if not failed_rows:
        return 0, 0, 0

    # Pre-fetch related references
    product = db.get(Product, batch.product_id) if batch.product_id else failed_rows[0].product
    quantity = db.get(Quantity, batch.quantity_id) if batch.quantity_id else failed_rows[0].quantity
    preset = (
        db.get(WhatsappPreset, batch.whatsapp_preset_id)
        if batch.whatsapp_preset_id
        else failed_rows[0].whatsapp_preset
    )

    synced, failed = _push_batch_to_zoho(db, batch, failed_rows, product, quantity, preset)
    return len(failed_rows), synced, failed
