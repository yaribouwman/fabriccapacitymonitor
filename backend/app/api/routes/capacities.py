from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.capacity import CapacityResponse, CapacitySnapshotResponse
from app.services import capacity_service

router = APIRouter()


@router.get("/customers/{customer_id}/capacities", response_model=list[CapacityResponse])
async def list_capacities(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    capacities = await capacity_service.get_capacities_by_customer(db, customer_id)
    return capacities


@router.get(
    "/customers/{customer_id}/capacities/{capacity_id}/snapshots",
    response_model=list[CapacitySnapshotResponse],
)
async def get_capacity_snapshots(
    customer_id: UUID,
    capacity_id: UUID,
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    snapshots = await capacity_service.get_snapshots(db, customer_id, capacity_id, start, end)
    return snapshots
