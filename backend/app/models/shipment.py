import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # tonne / MWh / m3
    shipment_date: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bill_of_lading: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reporting_period: Mapped[str] = mapped_column(String(7), nullable=False)  # 2026-Q1
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    product: Mapped["Product"] = relationship("Product", lazy="select")  # type: ignore
    supplier: Mapped["Supplier"] = relationship("Supplier", lazy="select")  # type: ignore
    calculation: Mapped["EmissionCalculation"] = relationship("EmissionCalculation", back_populates="shipment", uselist=False, lazy="select")


class EmissionCalculation(Base):
    __tablename__ = "emission_calculations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("shipments.id"), nullable=False)
    direct_emissions: Mapped[float | None] = mapped_column(Numeric(14, 6), nullable=True)
    indirect_emissions: Mapped[float | None] = mapped_column(Numeric(14, 6), nullable=True)
    embedded_emissions: Mapped[float | None] = mapped_column(Numeric(14, 6), nullable=True)
    emission_intensity: Mapped[float | None] = mapped_column(Numeric(14, 6), nullable=True)
    electricity_consumption: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    electricity_emission_factor: Mapped[float | None] = mapped_column(Numeric(12, 6), nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fuel_consumption: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    fuel_emission_factor: Mapped[float | None] = mapped_column(Numeric(12, 6), nullable=True)
    calculation_method: Mapped[str] = mapped_column(String(50), default="default")  # actual / default
    calculation_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="calculation")
