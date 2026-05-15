from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_superuser: bool

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
