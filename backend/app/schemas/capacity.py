from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CapacityResponse(BaseModel):
    id: UUID
    customer_id: UUID
    azure_resource_id: str
    display_name: str | None
    sku_name: str | None
    sku_tier: str | None
    location: str | None
    state: str | None
    last_synced_at: datetime | None

    model_config = {"from_attributes": True}


class CapacitySnapshotResponse(BaseModel):
    id: int
    capacity_id: UUID
    collected_at: datetime
    state: str
    sku_name: str

    model_config = {"from_attributes": True}
