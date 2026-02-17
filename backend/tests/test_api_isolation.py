import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.main import app
from app.schemas.customer import CustomerCreate
from app.services import customer_service, capacity_service


@pytest.mark.asyncio
async def test_snapshots_endpoint_blocks_cross_customer_access(db_session, override_get_db):
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

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/customers/{customer1.id}/capacities/{capacity1.id}/snapshots"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sku_name"] == "F2"

        response_cross = await client.get(
            f"/api/customers/{customer1.id}/capacities/{capacity2.id}/snapshots"
        )
        assert response_cross.status_code == 200
        data_cross = response_cross.json()
        assert len(data_cross) == 0


@pytest.mark.asyncio
async def test_metrics_endpoint_blocks_cross_customer_access(db_session, override_get_db):
    from datetime import datetime
    from app.models.metric import CapacityMetric

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

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/customers/{customer1.id}/capacities/{capacity1.id}/metrics"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["metric_name"] == "CPU"

        response_cross = await client.get(
            f"/api/customers/{customer1.id}/capacities/{capacity2.id}/metrics"
        )
        assert response_cross.status_code == 200
        data_cross = response_cross.json()
        assert len(data_cross) == 0


@pytest.mark.asyncio
async def test_ingest_endpoint_validates_customer_capacity_ownership(db_session, override_get_db):
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

    capacity2 = await capacity_service.upsert_capacity(
        db_session,
        customer2.id,
        "/subscriptions/yyy/resourceGroups/rg2/providers/Microsoft.Fabric/capacities/cap2",
        "customer2-capacity",
        "F4",
        "Standard",
        "westus",
        "Active",
    )

    payload = {
        "capacity_name": "customer2-capacity",
        "metrics": [
            {"name": "CPU", "value": 50.0, "aggregation": "Average"}
        ]
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ingest",
            json=payload,
            headers={"X-Ingest-Key": customer1.ingest_key}
        )
        assert response.status_code == 404
        assert "not found for this customer" in response.json()["detail"]
