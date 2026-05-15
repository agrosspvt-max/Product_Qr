from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.whatsapp_preset import WhatsappPreset
from app.schemas.whatsapp_preset import (
    WhatsappPresetCreate,
    WhatsappPresetOut,
    WhatsappPresetUpdate,
)

router = APIRouter(prefix="/whatsapp-presets", tags=["whatsapp-presets"])


def _clear_other_defaults(db: Session, keep_id: int | None) -> None:
    q = db.query(WhatsappPreset).filter(WhatsappPreset.is_default.is_(True))
    if keep_id is not None:
        q = q.filter(WhatsappPreset.id != keep_id)
    for row in q.all():
        row.is_default = False


@router.get("", response_model=List[WhatsappPresetOut])
def list_presets(
    only_active: bool = False,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> List[WhatsappPresetOut]:
    q = db.query(WhatsappPreset).order_by(
        WhatsappPreset.is_default.desc(), WhatsappPreset.preset_name.asc()
    )
    if only_active:
        q = q.filter(WhatsappPreset.is_active.is_(True))
    return [WhatsappPresetOut.model_validate(p) for p in q.all()]


@router.post("", response_model=WhatsappPresetOut, status_code=status.HTTP_201_CREATED)
def create_preset(
    payload: WhatsappPresetCreate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> WhatsappPresetOut:
    p = WhatsappPreset(
        preset_name=payload.preset_name.strip(),
        whatsapp_number=payload.whatsapp_number,
        is_default=payload.is_default,
        is_active=payload.is_active,
    )
    db.add(p)
    db.flush()
    if p.is_default:
        _clear_other_defaults(db, keep_id=p.id)
    db.commit()
    db.refresh(p)
    return WhatsappPresetOut.model_validate(p)


@router.put("/{preset_id}", response_model=WhatsappPresetOut)
def update_preset(
    preset_id: int,
    payload: WhatsappPresetUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> WhatsappPresetOut:
    p = db.get(WhatsappPreset, preset_id)
    if not p:
        raise HTTPException(404, "Preset not found")
    if payload.preset_name is not None:
        p.preset_name = payload.preset_name.strip()
    if payload.whatsapp_number is not None:
        p.whatsapp_number = payload.whatsapp_number
    if payload.is_active is not None:
        p.is_active = payload.is_active
    if payload.is_default is not None:
        p.is_default = payload.is_default
        if payload.is_default:
            _clear_other_defaults(db, keep_id=p.id)
    db.commit()
    db.refresh(p)
    return WhatsappPresetOut.model_validate(p)


# @router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_preset(
#     preset_id: int,
#     db: Session = Depends(get_db),
#     _: AdminUser = Depends(get_current_user),
# ) -> None:
#     p = db.get(WhatsappPreset, preset_id)
#     if not p:
#         raise HTTPException(404, "Preset not found")
#     p.is_active = False
#     db.commit()

from fastapi import Response, status

@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
):
    p = db.get(WhatsappPreset, preset_id)

    if not p:
        raise HTTPException(
            status_code=404,
            detail="Preset not found"
        )

    p.is_active = False
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
