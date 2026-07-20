import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Numeric, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # electricity / fuel / material
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(3), nullable=True, index=True)
    factor_value: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # MWh / tonne / GJ
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
