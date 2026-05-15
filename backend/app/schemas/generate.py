from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    product_id: int
    quantity_id: int
    manufacturing_month: int = Field(ge=1, le=12)
    manufacturing_year: int = Field(ge=2000, le=2099)
    whatsapp_preset_id: int
    count: int = Field(ge=1, le=100_000, description="Number of codes to generate (max 100k per batch)")


class GenerateResponse(BaseModel):
    batch_id: int
    batch_name: str
    total_requested: int
    total_generated: int
    zoho_synced: int
    zoho_failed: int
    excel_url: str
    sample_codes: List[str]


class BatchSummary(BaseModel):
    id: int
    batch_name: str
    total_codes: int
    zoho_synced: int
    zoho_failed: int
    product_name: str | None = None
    quantity_label: str | None = None
    manufacturing_month: int | None = None
    manufacturing_year: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class QRCodeOut(BaseModel):
    id: int
    code: str
    short_token: str
    short_link: str
    whatsapp_link: str
    zoho_sync_status: str
    zoho_record_id: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BatchDetail(BatchSummary):
    codes: List[QRCodeOut]


class RetryZohoResponse(BaseModel):
    retried: int
    synced: int
    failed: int
