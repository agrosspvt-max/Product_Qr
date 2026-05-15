from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WhatsappPreset(Base):
    __tablename__ = "whatsapp_presets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preset_name: Mapped[str] = mapped_column(String(150), nullable=False)
    whatsapp_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
