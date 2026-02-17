from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    client_id: Mapped[str] = mapped_column(String(36), nullable=False)
    client_secret_ref: Mapped[str] = mapped_column(Text, nullable=False)
    subscription_id: Mapped[str] = mapped_column(String(36), nullable=False)
    resource_group: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ingest_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    
    health_status: Mapped[str] = mapped_column(String(20), default="healthy", nullable=False)
    last_successful_collection: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_collection_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    capacities: Mapped[list["Capacity"]] = relationship(
        "Capacity", back_populates="customer", cascade="all, delete-orphan"
    )
    metrics: Mapped[list["CapacityMetric"]] = relationship(
        "CapacityMetric", back_populates="customer", cascade="all, delete-orphan"
    )
