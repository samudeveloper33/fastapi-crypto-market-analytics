from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, desc, select, text

from app.api.v1 import analytics, market, strategy
from app.core.config import get_settings
from app.core.database import get_db, init_db
from app.core.logging import get_logger, setup_logging
from app.models import MarketData
from app.tasks.scheduler import shutdown_scheduler, start_scheduler

load_dotenv()
setup_logging()

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Crypto Analytics API")
    init_db()
    start_scheduler()
    yield
    logger.info("Shutting down Crypto Analytics API")
    shutdown_scheduler()


app = FastAPI(
    title=settings.api_title,
    description="Crypto market data and analytics platform",
    version=settings.api_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(analytics.router)
app.include_router(strategy.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.exec(text("SELECT 1"))
        latest = db.exec(
            select(MarketData).order_by(desc(MarketData.timestamp))
        ).first()
        
        return {
            "status": "healthy",
            "database": "connected",
            "latest_data": latest.timestamp.isoformat() if latest else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
