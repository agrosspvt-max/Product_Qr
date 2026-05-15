from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.quantity import Quantity
from app.schemas.quantity import QuantityCreate, QuantityOut, QuantityUpdate

router = APIRouter(prefix="/quantities", tags=["quantities"])


@router.get("", response_model=List[QuantityOut])
def list_quantities(
    only_active: bool = False,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> List[QuantityOut]:
    q = db.query(Quantity).order_by(Quantity.label.asc())
    if only_active:
        q = q.filter(Quantity.is_active.is_(True))
    return [QuantityOut.model_validate(x) for x in q.all()]


@router.post("", response_model=QuantityOut, status_code=status.HTTP_201_CREATED)
def create_quantity(
    payload: QuantityCreate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> QuantityOut:
    q = Quantity(
        label=payload.label.strip(),
        internal_code=payload.internal_code,
        is_active=payload.is_active,
    )
    db.add(q)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail=f"internal_code '{payload.internal_code}' already exists")
    db.refresh(q)
    return QuantityOut.model_validate(q)


@router.put("/{quantity_id}", response_model=QuantityOut)
def update_quantity(
    quantity_id: int,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> QuantityOut:
    q = db.get(Quantity, quantity_id)
    if not q:
        raise HTTPException(404, "Quantity not found")
    if payload.label is not None:
        q.label = payload.label.strip()
    if payload.internal_code is not None:
        q.internal_code = payload.internal_code
    if payload.is_active is not None:
        q.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail="internal_code must be unique")
    db.refresh(q)
    return QuantityOut.model_validate(q)


# @router.delete("/{quantity_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_quantity(
#     quantity_id: int,
#     hard: bool = False,
#     db: Session = Depends(get_db),
#     _: AdminUser = Depends(get_current_user),
# ) -> None:
#     q = db.get(Quantity, quantity_id)
#     if not q:
#         raise HTTPException(404, "Quantity not found")
#     if hard:
#         try:
#             db.delete(q)
#             db.commit()
#         except IntegrityError:
#             db.rollback()
#             raise HTTPException(409, "Quantity is referenced — deactivate instead.")
#     else:
#         q.is_active = False
#         db.commit()

from fastapi import Response, status

@router.delete("/{quantity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quantity(
    quantity_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
):
    q = db.get(Quantity, quantity_id)

    if not q:
        raise HTTPException(
            status_code=404,
            detail="Quantity not found"
        )

    if hard:
        try:
            db.delete(q)
            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="Quantity is referenced — deactivate instead."
            )

    else:
        q.is_active = False
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
