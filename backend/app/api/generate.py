from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services import batch_service

router = APIRouter(tags=["generate"])


@router.post("/generate-codes", response_model=GenerateResponse)
def generate_codes(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user),
) -> GenerateResponse:
    try:
        batch, codes, synced, failed = batch_service.generate_batch(
            db,
            product_id=payload.product_id,
            quantity_id=payload.quantity_id,
            manufacturing_month=payload.manufacturing_month,
            manufacturing_year=payload.manufacturing_year,
            whatsapp_preset_id=payload.whatsapp_preset_id,
            count=payload.count,
            created_by=current_user,
        )
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(500, detail=str(exc))

    return GenerateResponse(
        batch_id=batch.id,
        batch_name=batch.batch_name,
        total_requested=payload.count,
        total_generated=len(codes),
        zoho_synced=synced,
        zoho_failed=failed,
        excel_url=f"/download-excel/{batch.id}",
        sample_codes=[c.code for c in codes[:5]],
    )
