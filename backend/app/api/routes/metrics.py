from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.metric import CapacityMetric
from app.schemas.metric import CapacityMetricResponse

router = APIRouter()


@router.get(
    "/customers/{customer_id}/capacities/{capacity_id}/metrics",
    response_model=list[CapacityMetricResponse],
)
async def get_capacity_metrics(
    customer_id: UUID,
    capacity_id: UUID,
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    metric_name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(CapacityMetric).where(
        CapacityMetric.customer_id == customer_id,
        CapacityMetric.capacity_id == capacity_id,
    )

    if start:
        query = query.where(CapacityMetric.collected_at >= start)
    if end:
        query = query.where(CapacityMetric.collected_at <= end)
    if metric_name:
        query = query.where(CapacityMetric.metric_name == metric_name)

    query = query.order_by(CapacityMetric.collected_at.desc()).limit(1000)

    metrics_query = await db.execute(query)
    metrics = metrics_query.scalars().all()
    return list(metrics)
