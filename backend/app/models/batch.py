from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GenerationBatch(Base):
    __tablename__ = "generation_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    total_codes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    zoho_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    zoho_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    excel_file_path: Mapped[str | None] = mapped_column(Text)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    quantity_id: Mapped[int | None] = mapped_column(ForeignKey("quantities.id"))
    whatsapp_preset_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_presets.id"))
    manufacturing_month: Mapped[int | None] = mapped_column(SmallInteger)
    manufacturing_year: Mapped[int | None] = mapped_column(SmallInteger)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    qr_codes = relationship(
        "QRCode", back_populates="batch", cascade="all, delete-orphan", lazy="select"
    )
