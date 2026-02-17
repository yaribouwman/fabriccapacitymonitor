from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, Float, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CapacityMetric(Base):
    __tablename__ = "capacity_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    capacity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capacities.id", ondelete="CASCADE"), nullable=False
    )
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    aggregation_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="metrics")
    capacity: Mapped["Capacity"] = relationship("Capacity", back_populates="metrics")

    __table_args__ = (
        Index("ix_metric_customer_time", "customer_id", "collected_at"),
        Index("ix_metric_capacity_name_time", "capacity_id", "metric_name", "collected_at"),
    )
