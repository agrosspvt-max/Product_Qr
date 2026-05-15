from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class WhatsappPresetBase(BaseModel):
    preset_name: str = Field(min_length=1, max_length=150)
    whatsapp_number: str = Field(min_length=8, max_length=20)
    is_default: bool = False
    is_active: bool = True

    @field_validator("whatsapp_number")
    @classmethod
    def _digits_only(cls, v: str) -> str:
        v = v.strip().lstrip("+")
        if not v.isdigit():
            raise ValueError("whatsapp_number must contain digits only (no + or spaces)")
        return v


class WhatsappPresetCreate(WhatsappPresetBase):
    pass


class WhatsappPresetUpdate(BaseModel):
    preset_name: str | None = None
    whatsapp_number: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None

    @field_validator("whatsapp_number")
    @classmethod
    def _digits_only(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lstrip("+")
        if not v.isdigit():
            raise ValueError("whatsapp_number must contain digits only")
        return v


class WhatsappPresetOut(WhatsappPresetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
