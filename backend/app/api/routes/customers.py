from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential
from app.core.config import settings
from app.db.session import get_db
from app.api.dependencies import verify_admin_key
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerListResponse
from app.services import customer_service
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customer = await customer_service.create_customer(db, customer_data)

    credential = DefaultAzureCredential()
    kv_client = SecretClient(vault_url=settings.azure_key_vault_url, credential=credential)
    
    try:
        await kv_client.set_secret(customer.client_secret_ref, customer_data.client_secret)
        logger.info("customer_secret_stored", customer_id=str(customer.id))
    finally:
        await kv_client.close()
        await credential.close()

    return customer


@router.get("/customers", response_model=list[CustomerListResponse])
async def list_customers(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customers = await customer_service.list_customers(db, active_only)
    return customers


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customer = await customer_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/customers/{customer_id}", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customer = await customer_service.deactivate_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/customers/{customer_id}/health")
async def get_customer_health(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customer = await customer_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "customer_id": str(customer.id),
        "customer_name": customer.name,
        "health_status": customer.health_status,
        "last_successful_collection": customer.last_successful_collection,
        "last_collection_error": customer.last_collection_error,
        "consecutive_failures": customer.consecutive_failures,
        "is_active": customer.is_active,
    }


@router.get("/customers/health/summary")
async def get_health_summary(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    customers = await customer_service.list_customers(db, active_only=True)
    
    summary = {
        "total_customers": len(customers),
        "healthy": sum(1 for c in customers if c.health_status == "healthy"),
        "degraded": sum(1 for c in customers if c.health_status == "degraded"),
        "critical": sum(1 for c in customers if c.health_status == "critical"),
        "customers_by_status": []
    }
    
    for customer in customers:
        if customer.health_status in ("degraded", "critical"):
            summary["customers_by_status"].append({
                "customer_id": str(customer.id),
                "customer_name": customer.name,
                "health_status": customer.health_status,
                "consecutive_failures": customer.consecutive_failures,
                "last_error": customer.last_collection_error,
            })
    
    return summary
