from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.dependencies import verify_ingest_key
from app.schemas.metric import IngestPayload
from app.services.capacity_service import get_capacity_by_name_and_customer
from app.models.metric import CapacityMetric
from app.models.customer import Customer
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/ingest", status_code=202)
async def ingest_metrics(
    payload: IngestPayload,
    customer: Customer = Depends(verify_ingest_key),
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        "ingest_request",
        customer_id=str(customer.id),
        capacity_name=payload.capacity_name,
        metric_count=len(payload.metrics),
    )

    capacity = await get_capacity_by_name_and_customer(db, customer.id, payload.capacity_name)
    if not capacity:
        logger.warning(
            "capacity_not_found",
            customer_id=str(customer.id),
            capacity_name=payload.capacity_name,
        )
        raise HTTPException(
            status_code=404,
            detail=f"Capacity '{payload.capacity_name}' not found for this customer",
        )

    collected_at = payload.collected_at or datetime.utcnow()

    for metric_data in payload.metrics:
        metric = CapacityMetric(
            customer_id=customer.id,
            capacity_id=capacity.id,
            collected_at=collected_at,
            metric_name=metric_data.name,
            metric_value=metric_data.value,
            aggregation_type=metric_data.aggregation,
        )
        db.add(metric)

    await db.commit()

    logger.info(
        "ingest_complete",
        customer_id=str(customer.id),
        capacity_id=str(capacity.id),
        metrics_stored=len(payload.metrics),
    )

    return {"status": "accepted", "metrics_stored": len(payload.metrics)}
