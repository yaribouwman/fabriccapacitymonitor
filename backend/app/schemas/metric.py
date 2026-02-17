from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MetricDataPoint(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float
    aggregation: str | None = None


class IngestPayload(BaseModel):
    capacity_name: str = Field(..., min_length=1)
    metrics: list[MetricDataPoint] = Field(..., min_items=1)
    collected_at: datetime | None = None


class CapacityMetricResponse(BaseModel):
    id: int
    customer_id: UUID
    capacity_id: UUID
    collected_at: datetime
    metric_name: str
    metric_value: float
    aggregation_type: str | None

    model_config = {"from_attributes": True}
