from __future__ import annotations

import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.batch import GenerationBatch
from app.models.product import Product
from app.models.qr_code import QRCode
from app.models.quantity import Quantity
from app.schemas.generate import (
    BatchDetail,
    BatchSummary,
    QRCodeOut,
    RetryZohoResponse,
)
from app.services import batch_service
from app.services.excel_export import export_batch_to_excel

router = APIRouter(tags=["batches"])


def _summary(b: GenerationBatch, product: Product | None, quantity: Quantity | None) -> BatchSummary:
    return BatchSummary(
        id=b.id,
        batch_name=b.batch_name,
        total_codes=b.total_codes,
        zoho_synced=b.zoho_synced,
        zoho_failed=b.zoho_failed,
        product_name=product.name if product else None,
        quantity_label=quantity.label if quantity else None,
        manufacturing_month=b.manufacturing_month,
        manufacturing_year=b.manufacturing_year,
        created_at=b.created_at,
    )


@router.get("/batches", response_model=List[BatchSummary])
def list_batches(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> List[BatchSummary]:
    rows = (
        db.query(GenerationBatch, Product, Quantity)
        .outerjoin(Product, Product.id == GenerationBatch.product_id)
        .outerjoin(Quantity, Quantity.id == GenerationBatch.quantity_id)
        .order_by(GenerationBatch.created_at.desc())
        .all()
    )
    return [_summary(b, p, q) for b, p, q in rows]


@router.get("/batch/{batch_id}", response_model=BatchDetail)
def batch_detail(
    batch_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> BatchDetail:
    batch = db.get(GenerationBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")

    codes = (
        db.query(QRCode)
        .options(joinedload(QRCode.product), joinedload(QRCode.quantity))
        .filter(QRCode.batch_id == batch_id)
        .order_by(QRCode.id.asc())
        .all()
    )

    product = db.get(Product, batch.product_id) if batch.product_id else None
    quantity = db.get(Quantity, batch.quantity_id) if batch.quantity_id else None

    return BatchDetail(
        **_summary(batch, product, quantity).model_dump(),
        codes=[QRCodeOut.model_validate(c) for c in codes],
    )


@router.get("/download-excel/{batch_id}")
def download_excel(
    batch_id: int,
    db: Session = Depends(get_db),
    # _: AdminUser = Depends(get_current_user),
):
    batch = db.get(GenerationBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")

    path = batch.excel_file_path
    if not path or not os.path.exists(path):
        # Regenerate on-demand if the file was deleted from disk
        codes = (
            db.query(QRCode)
            .options(joinedload(QRCode.product), joinedload(QRCode.quantity), joinedload(QRCode.whatsapp_preset))
            .filter(QRCode.batch_id == batch_id)
            .all()
        )
        if not codes:
            raise HTTPException(404, "Batch has no codes to export")
        path = export_batch_to_excel(batch.batch_name, codes)
        batch.excel_file_path = path
        db.commit()

    filename = os.path.basename(path)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@router.post("/batch/{batch_id}/retry-zoho", response_model=RetryZohoResponse)
def retry_zoho(
    batch_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> RetryZohoResponse:
    try:
        retried, synced, failed = batch_service.retry_failed_for_batch(db, batch_id)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc))
    return RetryZohoResponse(retried=retried, synced=synced, failed=failed)
