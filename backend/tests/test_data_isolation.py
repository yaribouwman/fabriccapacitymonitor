import pytest
from uuid import uuid4
from datetime import datetime
from app.schemas.customer import CustomerCreate
from app.services import customer_service, capacity_service
from app.models.capacity import CapacitySnapshot
from app.models.metric import CapacityMetric


@pytest.mark.asyncio
async def test_snapshots_customer_isolation(db_session):
    customer1_data = CustomerCreate(
        name="Customer A",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-a",
        subscription_id=str(uuid4()),
    )
    customer1 = await customer_service.create_customer(db_session, customer1_data)

    customer2_data = CustomerCreate(
        name="Customer B",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-b",
        subscription_id=str(uuid4()),
    )
    customer2 = await customer_service.create_customer(db_session, customer2_data)

    capacity1 = await capacity_service.upsert_capacity(
        db_session,
        customer1.id,
        "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Fabric/capacities/cap1",
        "Capacity 1",
        "F2",
        "Standard",
        "eastus",
        "Active",
    )

    capacity2 = await capacity_service.upsert_capacity(
        db_session,
        customer2.id,
        "/subscriptions/yyy/resourceGroups/rg2/providers/Microsoft.Fabric/capacities/cap2",
        "Capacity 2",
        "F4",
        "Standard",
        "westus",
        "Active",
    )

    await capacity_service.create_snapshot(db_session, capacity1.id, "Active", "F2")
    await capacity_service.create_snapshot(db_session, capacity2.id, "Active", "F4")

    snapshots_customer1 = await capacity_service.get_snapshots(
        db_session, customer1.id, capacity1.id, None, None
    )
    assert len(snapshots_customer1) == 1
    assert snapshots_customer1[0].sku_name == "F2"

    snapshots_customer1_wrong_capacity = await capacity_service.get_snapshots(
        db_session, customer1.id, capacity2.id, None, None
    )
    assert len(snapshots_customer1_wrong_capacity) == 0


@pytest.mark.asyncio
async def test_metrics_customer_isolation(db_session):
    customer1_data = CustomerCreate(
        name="Customer A",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-a",
        subscription_id=str(uuid4()),
    )
    customer1 = await customer_service.create_customer(db_session, customer1_data)

    customer2_data = CustomerCreate(
        name="Customer B",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-b",
        subscription_id=str(uuid4()),
    )
    customer2 = await customer_service.create_customer(db_session, customer2_data)

    capacity1 = await capacity_service.upsert_capacity(
        db_session,
        customer1.id,
        "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Fabric/capacities/cap1",
        "Capacity 1",
        "F2",
        "Standard",
        "eastus",
        "Active",
    )

    capacity2 = await capacity_service.upsert_capacity(
        db_session,
        customer2.id,
        "/subscriptions/yyy/resourceGroups/rg2/providers/Microsoft.Fabric/capacities/cap2",
        "Capacity 2",
        "F4",
        "Standard",
        "westus",
        "Active",
    )

    metric1 = CapacityMetric(
        customer_id=customer1.id,
        capacity_id=capacity1.id,
        collected_at=datetime.utcnow(),
        metric_name="CPU",
        metric_value=75.5,
        aggregation_type="Average",
    )
    db_session.add(metric1)

    metric2 = CapacityMetric(
        customer_id=customer2.id,
        capacity_id=capacity2.id,
        collected_at=datetime.utcnow(),
        metric_name="Memory",
        metric_value=80.0,
        aggregation_type="Average",
    )
    db_session.add(metric2)

    await db_session.commit()

    from sqlalchemy import select
    from app.models.metric import CapacityMetric

    query1 = select(CapacityMetric).where(
        CapacityMetric.customer_id == customer1.id,
        CapacityMetric.capacity_id == capacity1.id,
    )
    result1 = await db_session.execute(query1)
    metrics1 = result1.scalars().all()
    assert len(metrics1) == 1
    assert metrics1[0].metric_name == "CPU"

    query2 = select(CapacityMetric).where(
        CapacityMetric.customer_id == customer1.id,
        CapacityMetric.capacity_id == capacity2.id,
    )
    result2 = await db_session.execute(query2)
    metrics2 = result2.scalars().all()
    assert len(metrics2) == 0


@pytest.mark.asyncio
async def test_capacity_by_name_customer_isolation(db_session):
    customer1_data = CustomerCreate(
        name="Customer A",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-a",
        subscription_id=str(uuid4()),
    )
    customer1 = await customer_service.create_customer(db_session, customer1_data)

    customer2_data = CustomerCreate(
        name="Customer B",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret-b",
        subscription_id=str(uuid4()),
    )
    customer2 = await customer_service.create_customer(db_session, customer2_data)

    await capacity_service.upsert_capacity(
        db_session,
        customer1.id,
        "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Fabric/capacities/shared-name",
        "shared-name",
        "F2",
        "Standard",
        "eastus",
        "Active",
    )

    await capacity_service.upsert_capacity(
        db_session,
        customer2.id,
        "/subscriptions/yyy/resourceGroups/rg2/providers/Microsoft.Fabric/capacities/shared-name",
        "shared-name",
        "F4",
        "Standard",
        "westus",
        "Active",
    )

    capacity_customer1 = await capacity_service.get_capacity_by_name_and_customer(
        db_session, customer1.id, "shared-name"
    )
    assert capacity_customer1 is not None
    assert capacity_customer1.sku_name == "F2"

    capacity_customer2 = await capacity_service.get_capacity_by_name_and_customer(
        db_session, customer2.id, "shared-name"
    )
    assert capacity_customer2 is not None
    assert capacity_customer2.sku_name == "F4"

    assert capacity_customer1.id != capacity_customer2.id


@pytest.mark.asyncio
async def test_cascading_delete_customer_data(db_session):
    customer_data = CustomerCreate(
        name="Customer to Delete",
        tenant_id=str(uuid4()),
        client_id=str(uuid4()),
        client_secret="secret",
        subscription_id=str(uuid4()),
    )
    customer = await customer_service.create_customer(db_session, customer_data)

    capacity = await capacity_service.upsert_capacity(
        db_session,
        customer.id,
        "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Fabric/capacities/cap1",
        "Capacity 1",
        "F2",
        "Standard",
        "eastus",
        "Active",
    )

    await capacity_service.create_snapshot(db_session, capacity.id, "Active", "F2")

    metric = CapacityMetric(
        customer_id=customer.id,
        capacity_id=capacity.id,
        collected_at=datetime.utcnow(),
        metric_name="CPU",
        metric_value=75.5,
        aggregation_type="Average",
    )
    db_session.add(metric)
    await db_session.commit()

    from sqlalchemy import select, delete
    from app.models.customer import Customer

    await db_session.execute(delete(Customer).where(Customer.id == customer.id))
    await db_session.commit()

    from app.models.capacity import Capacity
    capacity_query = await db_session.execute(
        select(Capacity).where(Capacity.customer_id == customer.id)
    )
    capacities = capacity_query.scalars().all()
    assert len(capacities) == 0

    from app.models.metric import CapacityMetric
    metric_query = await db_session.execute(
        select(CapacityMetric).where(CapacityMetric.customer_id == customer.id)
    )
    metrics = metric_query.scalars().all()
    assert len(metrics) == 0
