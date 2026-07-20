import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class HSCode(Base):
    __tablename__ = "hs_codes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cn_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sector: Mapped[str] = mapped_column(String(50), nullable=False)  # steel / aluminium / cement / fertilizer / electricity / hydrogen
    cbam_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reporting_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
