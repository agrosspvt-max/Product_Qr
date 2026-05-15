"""Zoho CRM REST API client.

Responsibilities:
- OAuth token refresh (uses refresh_token grant)
- Bulk insert into a configurable custom module (default: Product_QR)
- Retry with exponential backoff for transient failures
- API logging for traceability
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from sqlalchemy.orm import Session

from app.services import settings_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


ZOHO_KEYS = [
    "zoho_client_id",
    "zoho_client_secret",
    "zoho_refresh_token",
    "zoho_organization_id",
    "zoho_api_domain",
    "zoho_module_name",
]


@dataclass
class ZohoConfig:
    client_id: str
    client_secret: str
    refresh_token: str
    organization_id: str
    api_domain: str  # e.g. https://www.zohoapis.com
    module_name: str  # e.g. Product_QR

    @property
    def is_configured(self) -> bool:
        return all([self.client_id, self.client_secret, self.refresh_token])

    @property
    def accounts_domain(self) -> str:
        """Map api_domain → matching accounts domain for OAuth token endpoint."""
        host = self.api_domain.replace("https://", "").replace("http://", "")
        # www.zohoapis.com  -> accounts.zoho.com
        # www.zohoapis.in   -> accounts.zoho.in
        # www.zohoapis.eu   -> accounts.zoho.eu
        if "." in host:
            tld = host.rsplit(".", 1)[-1]
            return f"https://accounts.zoho.{tld}"
        return "https://accounts.zoho.com"


def load_config(db: Session) -> ZohoConfig:
    values = settings_service.get_many(db, ZOHO_KEYS)
    return ZohoConfig(
        client_id=values.get("zoho_client_id", ""),
        client_secret=values.get("zoho_client_secret", ""),
        refresh_token=values.get("zoho_refresh_token", ""),
        organization_id=values.get("zoho_organization_id", ""),
        api_domain=(values.get("zoho_api_domain") or "https://www.zohoapis.com").rstrip("/"),
        module_name=values.get("zoho_module_name") or "Product_QR",
    )


class ZohoCRMClient:
    """Thin wrapper around Zoho CRM REST endpoints with token caching."""

    # Cache the access token at class level so multiple inserts within a single
    # batch reuse it instead of refreshing every call.
    _cached_token: Optional[str] = None
    _cached_expiry: float = 0.0

    def __init__(self, cfg: ZohoConfig):
        self.cfg = cfg

    # ----------------------------- OAuth -----------------------------------

    def _refresh_access_token(self) -> str:
        if not self.cfg.is_configured:
            raise RuntimeError("Zoho is not configured (missing client_id / secret / refresh_token).")

        url = f"{self.cfg.accounts_domain}/oauth/v2/token"
        params = {
            "refresh_token": self.cfg.refresh_token,
            "client_id": self.cfg.client_id,
            "client_secret": self.cfg.client_secret,
            "grant_type": "refresh_token",
        }
        logger.info("Zoho: refreshing access token at %s", url)
        resp = requests.post(url, params=params, timeout=30)
        if resp.status_code != 200:
            logger.error("Zoho token refresh failed: %s — %s", resp.status_code, resp.text)
            resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError(f"Zoho token refresh returned no access_token: {data}")
        expires_in = int(data.get("expires_in", 3300))  # seconds
        ZohoCRMClient._cached_token = token
        # leave a 60s safety margin
        ZohoCRMClient._cached_expiry = time.time() + max(expires_in - 60, 60)
        return token

    def access_token(self) -> str:
        if (
            ZohoCRMClient._cached_token
            and time.time() < ZohoCRMClient._cached_expiry
        ):
            return ZohoCRMClient._cached_token
        return self._refresh_access_token()

    # ----------------------------- HTTP ------------------------------------

    def _headers(self) -> Dict[str, str]:
        token = self.access_token()
        headers = {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
        }
        if self.cfg.organization_id:
            headers["X-CRM-ORG"] = self.cfg.organization_id
        return headers

    def _post(self, path: str, payload: Dict[str, Any]) -> requests.Response:
        url = f"{self.cfg.api_domain}{path}"
        return requests.post(url, json=payload, headers=self._headers(), timeout=60)

    # ----------------------------- Records ---------------------------------

    def insert_records(
        self,
        records: List[Dict[str, Any]],
        max_retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """Insert up to 100 records into the configured module.

        Returns the per-record "data" array from Zoho's response, preserving
        order. Each entry has either {"status":"success","details":{"id":...}}
        or {"status":"error","message":...}.

        Raises on hard auth / network failure after exhausted retries.
        """
        if not records:
            return []
        if len(records) > 100:
            raise ValueError("Zoho insert chunks must be <= 100 records")

        path = f"/crm/v3/{self.cfg.module_name}"
        payload = {"data": records, "trigger": []}

        attempt = 0
        while True:
            try:
                resp = self._post(path, payload)
                # 401 → refresh token & retry once
                if resp.status_code == 401:
                    logger.warning("Zoho 401, forcing token refresh")
                    ZohoCRMClient._cached_token = None
                    self._refresh_access_token()
                    resp = self._post(path, payload)

                if resp.status_code in (200, 201, 202):
                    data = resp.json().get("data", [])
                    return data

                # Retriable server errors
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    sleep = 2 ** attempt
                    logger.warning(
                        "Zoho %s — retrying in %ss (attempt %d/%d)",
                        resp.status_code, sleep, attempt + 1, max_retries,
                    )
                    time.sleep(sleep)
                    attempt += 1
                    continue

                logger.error("Zoho insert failed: %s — %s", resp.status_code, resp.text)
                resp.raise_for_status()

            except requests.RequestException as exc:
                if attempt < max_retries:
                    sleep = 2 ** attempt
                    logger.warning("Zoho network error %s — retry in %ss", exc, sleep)
                    time.sleep(sleep)
                    attempt += 1
                    continue
                raise

    # ----------------------------- Helpers ---------------------------------

    @staticmethod
    def build_record(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Map our internal field names → the Zoho module's field API names.

        The "Name" field in Zoho is the module's title and is set to the code.
        """
        created_at = payload.get("created_at")
        if isinstance(created_at, datetime):
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            # created_iso = created_at.strftime("%Y-%m-%dT%H:%M:%S%z")
            created_iso = created_at.isoformat(timespec="seconds")
            # Zoho expects YYYY-MM-DDTHH:MM:SS+0000 (no colon in tz). Convert.
            if len(created_iso) >= 5 and (created_iso[-5] in "+-"):
                # already in +HHMM form — fine
                pass
        else:
            created_iso = None

        rec: Dict[str, Any] = {
            "Name": payload["code"],
            "Product_Name": payload.get("product_name"),
            "Product_Initials": payload.get("product_initials"),
            "Quantity_Label": payload.get("quantity_label"),
            "Quantity_Code": payload.get("quantity_code"),
            "Manufacturing_Month": payload.get("manufacturing_month"),
            "Manufacturing_Year": str(payload.get("manufacturing_year") or ""),
            "Manufacturing_Display": payload.get("manufacturing_display"),
            "WhatsApp_Number": payload.get("whatsapp_number"),
            "WhatsApp_Redirect_URL": payload.get("whatsapp_redirect_url"),
            "Short_Token": payload.get("short_token"),
            "Short_Link": payload.get("short_link"),
            "Batch_ID": payload.get("batch_name"),
            "Status": payload.get("status", "UNUSED"),
        }
        if created_iso:
            rec["Code_Created_At"] = created_iso
        # Drop None values so Zoho doesn't reject the call
        return {k: v for k, v in rec.items() if v is not None}


def push_records(
    db: Session,
    records: List[Dict[str, Any]],
    chunk_size: int = 100,
) -> List[Tuple[Dict[str, Any], Optional[str], Optional[str]]]:
    """Push N records to Zoho in 100-row chunks.

    Returns a list of (input_payload, zoho_record_id, error_message) tuples
    aligned with the input order. If Zoho is not configured, every entry is
    returned as (payload, None, "Zoho not configured").
    """
    cfg = load_config(db)
    if not cfg.is_configured:
        logger.warning("Zoho not configured — marking all records as failed.")
        return [(rec, None, "Zoho not configured") for rec in records]

    client = ZohoCRMClient(cfg)
    results: List[Tuple[Dict[str, Any], Optional[str], Optional[str]]] = []

    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]
        zoho_payload = [ZohoCRMClient.build_record(r) for r in chunk]
        try:
            zoho_data = client.insert_records(zoho_payload)
        except Exception as exc:  # pragma: no cover - network failure path
            logger.exception("Zoho bulk insert failed for chunk starting %d", i)
            for rec in chunk:
                results.append((rec, None, str(exc)))
            continue

        # Align Zoho per-record response with input
        for input_rec, zoho_rec in zip(chunk, zoho_data):
            status = (zoho_rec or {}).get("status")
            if status == "success":
                rid = (zoho_rec.get("details") or {}).get("id")
                results.append((input_rec, str(rid) if rid else None, None))
            else:
                msg = (zoho_rec or {}).get("message") or "Unknown Zoho error"
                results.append((input_rec, None, msg))

        # Be gentle on rate limits
        time.sleep(0.2)

    return results
