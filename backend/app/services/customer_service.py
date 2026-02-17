import secrets
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
    ingest_key = secrets.token_urlsafe(48)
    
    customer = Customer(
        name=customer_data.name,
        tenant_id=customer_data.tenant_id,
        client_id=customer_data.client_id,
        client_secret_ref=f"customer-{customer_data.tenant_id}-secret",
        subscription_id=customer_data.subscription_id,
        resource_group=customer_data.resource_group,
        ingest_key=ingest_key,
    )
    
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def get_customer(db: AsyncSession, customer_id: UUID) -> Customer | None:
    customer_query = await db.execute(select(Customer).where(Customer.id == customer_id))
    return customer_query.scalars().first()


async def get_customer_by_ingest_key(db: AsyncSession, ingest_key: str) -> Customer | None:
    customer_query = await db.execute(select(Customer).where(Customer.ingest_key == ingest_key))
    return customer_query.scalars().first()


async def list_customers(db: AsyncSession, active_only: bool = False) -> list[Customer]:
    query = select(Customer)
    if active_only:
        query = query.where(Customer.is_active == True)
    customers_query = await db.execute(query.order_by(Customer.created_at.desc()))
    return list(customers_query.scalars().all())


async def deactivate_customer(db: AsyncSession, customer_id: UUID) -> Customer | None:
    customer = await get_customer(db, customer_id)
    if customer:
        customer.is_active = False
        await db.commit()
        await db.refresh(customer)
    return customer
