from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(AdminUser).filter(AdminUser.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    token = create_access_token(user.id, extra={"email": user.email})
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(current: AdminUser = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current)
