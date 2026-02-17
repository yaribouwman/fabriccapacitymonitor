from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, UniqueConstraint, func, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Capacity(Base):
    __tablename__ = "capacities"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    azure_resource_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    sku_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sku_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="capacities")
    snapshots: Mapped[list["CapacitySnapshot"]] = relationship(
        "CapacitySnapshot", back_populates="capacity", cascade="all, delete-orphan"
    )
    metrics: Mapped[list["CapacityMetric"]] = relationship(
        "CapacityMetric", back_populates="capacity", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("customer_id", "azure_resource_id", name="uq_customer_resource"),
    )


class CapacitySnapshot(Base):
    __tablename__ = "capacity_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    capacity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capacities.id", ondelete="CASCADE"), nullable=False
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    sku_name: Mapped[str] = mapped_column(String(20), nullable=False)

    capacity: Mapped["Capacity"] = relationship("Capacity", back_populates="snapshots")

    __table_args__ = (
        Index("ix_snapshot_capacity_time", "capacity_id", "collected_at"),
    )
