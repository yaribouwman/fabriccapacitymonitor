from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.capacity import Capacity, CapacitySnapshot


async def upsert_capacity(
    db: AsyncSession,
    customer_id: UUID,
    azure_resource_id: str,
    display_name: str | None,
    sku_name: str | None,
    sku_tier: str | None,
    location: str | None,
    state: str | None,
) -> Capacity:
    capacity_query = await db.execute(
        select(Capacity).where(Capacity.azure_resource_id == azure_resource_id)
    )
    capacity = capacity_query.scalars().first()

    if capacity:
        capacity.display_name = display_name
        capacity.sku_name = sku_name
        capacity.sku_tier = sku_tier
        capacity.location = location
        capacity.state = state
        capacity.last_synced_at = datetime.utcnow()
    else:
        capacity = Capacity(
            customer_id=customer_id,
            azure_resource_id=azure_resource_id,
            display_name=display_name,
            sku_name=sku_name,
            sku_tier=sku_tier,
            location=location,
            state=state,
            last_synced_at=datetime.utcnow(),
        )
        db.add(capacity)

    await db.commit()
    await db.refresh(capacity)
    return capacity


async def create_snapshot(
    db: AsyncSession, capacity_id: UUID, state: str, sku_name: str
) -> CapacitySnapshot:
    snapshot = CapacitySnapshot(capacity_id=capacity_id, state=state, sku_name=sku_name)
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def get_capacities_by_customer(db: AsyncSession, customer_id: UUID) -> list[Capacity]:
    capacities_query = await db.execute(
        select(Capacity)
        .where(Capacity.customer_id == customer_id)
        .order_by(Capacity.display_name)
    )
    return list(capacities_query.scalars().all())


async def get_capacity_by_name_and_customer(
    db: AsyncSession, customer_id: UUID, capacity_name: str
) -> Capacity | None:
    capacity_query = await db.execute(
        select(Capacity)
        .where(Capacity.customer_id == customer_id)
        .where(Capacity.display_name == capacity_name)
    )
    return capacity_query.scalars().first()


async def get_snapshots(
    db: AsyncSession, customer_id: UUID, capacity_id: UUID, start: datetime | None, end: datetime | None
) -> list[CapacitySnapshot]:
    capacity_query = await db.execute(
        select(Capacity).where(
            Capacity.id == capacity_id,
            Capacity.customer_id == customer_id
        )
    )
    capacity = capacity_query.scalars().first()
    
    if not capacity:
        return []
    
    query = select(CapacitySnapshot).where(CapacitySnapshot.capacity_id == capacity_id)
    
    if start:
        query = query.where(CapacitySnapshot.collected_at >= start)
    if end:
        query = query.where(CapacitySnapshot.collected_at <= end)
    
    query = query.order_by(CapacitySnapshot.collected_at.desc())
    
    snapshots_query = await db.execute(query)
    return list(snapshots_query.scalars().all())
