from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
def list_products(
    only_active: bool = False,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> List[ProductOut]:
    q = db.query(Product).order_by(Product.name.asc())
    if only_active:
        q = q.filter(Product.is_active.is_(True))
    return [ProductOut.model_validate(p) for p in q.all()]


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ProductOut:
    p = Product(name=payload.name.strip(), initials=payload.initials, is_active=payload.is_active)
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail=f"Initials '{payload.initials}' already exist")
    db.refresh(p)
    return ProductOut.model_validate(p)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ProductOut:
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    if payload.name is not None:
        p.name = payload.name.strip()
    if payload.initials is not None:
        p.initials = payload.initials
    if payload.is_active is not None:
        p.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail="Initials must be unique")
    db.refresh(p)
    return ProductOut.model_validate(p)


from fastapi import APIRouter, Response, status, HTTPException, Depends

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
):
    p = db.get(Product, product_id)

    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    if hard:
        try:
            db.delete(p)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Product is referenced by existing codes; deactivate instead."
            )
    else:
        p.is_active = False
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
