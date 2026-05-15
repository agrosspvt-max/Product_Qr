from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CHAR,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(CHAR(15), unique=True, nullable=False, index=True)
    short_token: Mapped[str] = mapped_column(String(7), unique=True, nullable=False, index=True)
    short_link: Mapped[str] = mapped_column(Text, nullable=False)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False)
    manufacturing_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    manufacturing_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    whatsapp_preset_id: Mapped[int] = mapped_column(
        ForeignKey("whatsapp_presets.id"), nullable=False
    )
    whatsapp_link: Mapped[str] = mapped_column(Text, nullable=False)

    zoho_record_id: Mapped[str | None] = mapped_column(String(50))
    zoho_sync_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)
    zoho_last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    zoho_error: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="UNUSED", nullable=False)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("generation_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    batch = relationship("GenerationBatch", back_populates="qr_codes")
    product = relationship("Product", lazy="joined")
    quantity = relationship("Quantity", lazy="joined")
    whatsapp_preset = relationship("WhatsappPreset", lazy="joined")
