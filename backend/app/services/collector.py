import asyncio
from datetime import datetime
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.storage.blob.aio import BlobServiceClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.config import settings
from app.services.azure_client import AzureClient
from app.services.customer_service import list_customers
from app.services.capacity_service import upsert_capacity, create_snapshot
from app.models.customer import Customer
import structlog
import httpx

logger = structlog.get_logger()


class CapacityCollector:
    def __init__(self):
        self.azure_client = AzureClient()
        self.kv_client: SecretClient | None = None
        self.blob_client: BlobServiceClient | None = None
        self.lease_blob_name = "collector-lock"
        self.lease_duration = 60

    async def initialize(self):
        credential = DefaultAzureCredential()
        self.kv_client = SecretClient(vault_url=settings.azure_key_vault_url, credential=credential)
        
        if settings.azure_storage_connection_string:
            self.blob_client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )

    async def close(self):
        await self.azure_client.close()
        if self.kv_client:
            await self.kv_client.close()
        if self.blob_client:
            await self.blob_client.close()
    
    async def acquire_lock(self) -> str | None:
        if not self.blob_client:
            logger.warning("distributed_locking_disabled", reason="no_storage_connection_string")
            return None
            
        try:
            container_client = self.blob_client.get_container_client("locks")
            
            try:
                await container_client.create_container()
                logger.info("lock_container_created")
            except Exception:
                pass
            
            blob_client = container_client.get_blob_client(self.lease_blob_name)
            
            try:
                await blob_client.upload_blob(b"lock", overwrite=False)
            except Exception:
                pass
            
            lease_client = blob_client.get_blob_lease_client()
            lease_id = await lease_client.acquire(lease_duration=self.lease_duration)
            logger.info("distributed_lock_acquired", lease_id=lease_id)
            return lease_id
            
        except Exception as e:
            logger.warning("failed_to_acquire_lock", error=str(e))
            return None
    
    async def release_lock(self, lease_id: str | None):
        if not lease_id or not self.blob_client:
            return
            
        try:
            container_client = self.blob_client.get_container_client("locks")
            blob_client = container_client.get_blob_client(self.lease_blob_name)
            lease_client = blob_client.get_blob_lease_client(lease_id)
            await lease_client.release()
            logger.info("distributed_lock_released", lease_id=lease_id)
        except Exception as e:
            logger.warning("failed_to_release_lock", error=str(e))

    async def update_customer_health(
        self, db: AsyncSession, customer_id, success: bool, error_message: str | None = None
    ):
        try:
            if success:
                await db.execute(
                    update(Customer)
                    .where(Customer.id == customer_id)
                    .values(
                        health_status="healthy",
                        last_successful_collection=datetime.utcnow(),
                        last_collection_error=None,
                        consecutive_failures=0,
                    )
                )
            else:
                result = await db.execute(
                    select(Customer).where(Customer.id == customer_id)
                )
                customer = result.scalar_one()
                new_failures = customer.consecutive_failures + 1
                
                health_status = "healthy"
                if new_failures >= 3:
                    health_status = "degraded"
                if new_failures >= 5:
                    health_status = "critical"
                
                await db.execute(
                    update(Customer)
                    .where(Customer.id == customer_id)
                    .values(
                        health_status=health_status,
                        last_collection_error=error_message[:1000] if error_message else None,
                        consecutive_failures=new_failures,
                    )
                )
            
            await db.commit()
            
        except Exception as e:
            logger.error("failed_to_update_customer_health", customer_id=str(customer_id), error=str(e))

    async def collect_for_customer(self, db: AsyncSession, customer):
        error_type = "unknown"
        error_message = None
        
        try:
            logger.info("collecting_capacities", customer_id=str(customer.id), customer_name=customer.name)

            secret = await self.kv_client.get_secret(customer.client_secret_ref)
            client_secret = secret.value

            token = await self.azure_client.get_token(
                customer.tenant_id, customer.client_id, client_secret
            )

            capacities = await self.azure_client.list_capacities(
                token, customer.subscription_id, customer.resource_group
            )

            logger.info(
                "capacities_discovered",
                customer_id=str(customer.id),
                count=len(capacities),
            )

            for cap_data in capacities:
                capacity = await upsert_capacity(
                    db,
                    customer.id,
                    cap_data["id"],
                    cap_data.get("name"),
                    cap_data.get("sku", {}).get("name"),
                    cap_data.get("sku", {}).get("tier"),
                    cap_data.get("location"),
                    cap_data.get("properties", {}).get("state"),
                )

                await create_snapshot(
                    db,
                    capacity.id,
                    capacity.state or "Unknown",
                    capacity.sku_name or "Unknown",
                )

            await self.update_customer_health(db, customer.id, success=True)
            logger.info("collection_complete", customer_id=str(customer.id))

        except ClientAuthenticationError as e:
            error_type = "authentication_failed"
            error_message = f"Service Principal authentication failed. Secret may be expired or invalid: {str(e)}"
            logger.error(
                error_type,
                customer_id=str(customer.id),
                customer_name=customer.name,
                tenant_id=customer.tenant_id,
                client_id=customer.client_id,
                error=str(e),
            )
            await self.update_customer_health(db, customer.id, success=False, error_message=error_message)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                error_type = "authorization_failed"
                error_message = f"Azure API authorization failed (HTTP {e.response.status_code}). Check Service Principal permissions."
            else:
                error_type = "api_error"
                error_message = f"Azure API error (HTTP {e.response.status_code}): {e.response.text[:500]}"
            
            logger.error(
                error_type,
                customer_id=str(customer.id),
                customer_name=customer.name,
                status_code=e.response.status_code,
                error=str(e),
            )
            await self.update_customer_health(db, customer.id, success=False, error_message=error_message)
            
        except Exception as e:
            error_type = "collection_failed"
            error_message = f"Unexpected error: {str(e)}"
            logger.error(
                error_type,
                customer_id=str(customer.id),
                customer_name=customer.name,
                error=str(e),
            )
            await self.update_customer_health(db, customer.id, success=False, error_message=error_message)

    async def run_collection(self, db: AsyncSession):
        lease_id = None
        
        try:
            lease_id = await self.acquire_lock()
            
            if lease_id is None and self.blob_client is not None:
                logger.info("collection_skipped", reason="another_instance_holds_lock")
                return
            
            logger.info("collection_cycle_start")
            customers = await list_customers(db, active_only=True)
            logger.info("active_customers", count=len(customers))

            semaphore = asyncio.Semaphore(settings.collector_max_concurrency)
            
            async def collect_with_limit(customer):
                async with semaphore:
                    await self.collect_for_customer(db, customer)
            
            await asyncio.gather(
                *[collect_with_limit(customer) for customer in customers],
                return_exceptions=True
            )

            logger.info("collection_cycle_complete", customers_processed=len(customers))
            
        finally:
            if lease_id:
                await self.release_lock(lease_id)


async def run_collector_loop(interval_minutes: int):
    collector = CapacityCollector()
    await collector.initialize()

    try:
        while True:
            # Deferred import to avoid circular dependency with db module at startup
            from app.db.session import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                await collector.run_collection(db)
            
            await asyncio.sleep(interval_minutes * 60)
    finally:
        await collector.close()
