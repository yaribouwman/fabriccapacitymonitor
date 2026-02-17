from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.customer_service import get_customer_by_ingest_key
from app.core.config import settings


async def verify_ingest_key(
    x_ingest_key: str = Header(..., alias="X-Ingest-Key"),
    db: AsyncSession = Depends(get_db),
):
    customer = await get_customer_by_ingest_key(db, x_ingest_key)
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid ingest key")
    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")
    return customer


async def verify_admin_key(
    x_admin_key: str = Header(..., alias="X-Admin-Key"),
):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True
