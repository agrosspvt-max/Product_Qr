from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class QuantityBase(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    internal_code: str = Field(min_length=4, max_length=4)
    is_active: bool = True

    @field_validator("internal_code")
    @classmethod
    def _validate(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 4 or not v.isalnum():
            raise ValueError("internal_code must be exactly 4 alphanumeric chars")
        return v


class QuantityCreate(QuantityBase):
    pass


class QuantityUpdate(BaseModel):
    label: str | None = None
    internal_code: str | None = Field(default=None, min_length=4, max_length=4)
    is_active: bool | None = None

    @field_validator("internal_code")
    @classmethod
    def _validate(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().upper()
        if len(v) != 4 or not v.isalnum():
            raise ValueError("internal_code must be exactly 4 alphanumeric chars")
        return v


class QuantityOut(QuantityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
