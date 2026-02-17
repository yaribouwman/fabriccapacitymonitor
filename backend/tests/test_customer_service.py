import pytest
from app.schemas.customer import CustomerCreate
from app.services import customer_service


@pytest.mark.asyncio
async def test_create_customer(db_session):
    customer_data = CustomerCreate(
        name="Test Customer",
        tenant_id="00000000-0000-0000-0000-000000000000",
        client_id="11111111-1111-1111-1111-111111111111",
        client_secret="test-secret",
        subscription_id="22222222-2222-2222-2222-222222222222",
    )

    customer = await customer_service.create_customer(db_session, customer_data)

    assert customer.id is not None
    assert customer.name == "Test Customer"
    assert customer.tenant_id == customer_data.tenant_id
    assert customer.is_active is True
    assert len(customer.ingest_key) > 20


@pytest.mark.asyncio
async def test_list_customers(db_session):
    customer_data = CustomerCreate(
        name="Test Customer",
        tenant_id="00000000-0000-0000-0000-000000000000",
        client_id="11111111-1111-1111-1111-111111111111",
        client_secret="test-secret",
        subscription_id="22222222-2222-2222-2222-222222222222",
    )
    await customer_service.create_customer(db_session, customer_data)

    customers = await customer_service.list_customers(db_session)
    assert len(customers) == 1
    assert customers[0].name == "Test Customer"
