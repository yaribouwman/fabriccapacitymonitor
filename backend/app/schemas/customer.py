from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    tenant_id: str = Field(..., min_length=36, max_length=36)
    client_id: str = Field(..., min_length=36, max_length=36)
    client_secret: str = Field(..., min_length=1)
    subscription_id: str = Field(..., min_length=36, max_length=36)
    resource_group: str | None = None


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    tenant_id: str
    client_id: str
    subscription_id: str
    resource_group: str | None
    is_active: bool
    ingest_key: str
    health_status: str
    last_successful_collection: datetime | None
    last_collection_error: str | None
    consecutive_failures: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    health_status: str
    consecutive_failures: int
    last_successful_collection: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
