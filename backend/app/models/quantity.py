from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CHAR, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Quantity(Base):
    __tablename__ = "quantities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    internal_code: Mapped[str] = mapped_column(CHAR(4), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
