import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.core.config import settings
from app.api.routes import health, customers, capacities, metrics, ingest
from app.services.collector import run_collector_loop

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_startup", version=settings.app_version)
    
    collector_task = asyncio.create_task(
        run_collector_loop(settings.collector_interval_minutes)
    )
    
    yield
    
    logger.info("app_shutdown")
    collector_task.cancel()
    try:
        await collector_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Fabric Capacity Monitor",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(customers.router, prefix="/api", tags=["customers"])
app.include_router(capacities.router, prefix="/api", tags=["capacities"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
