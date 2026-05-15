from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    initials: str = Field(min_length=2, max_length=4)
    is_active: bool = True

    @field_validator("initials")
    @classmethod
    def _upper_alnum(cls, v: str) -> str:
        v = v.strip().upper()
        if not v.isalnum():
            raise ValueError("Initials must be alphanumeric (A-Z, 0-9)")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    initials: str | None = Field(default=None, min_length=2, max_length=4)
    is_active: bool | None = None

    @field_validator("initials")
    @classmethod
    def _upper_alnum(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().upper()
        if not v.isalnum():
            raise ValueError("Initials must be alphanumeric")
        return v


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
