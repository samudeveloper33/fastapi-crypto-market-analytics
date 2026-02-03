from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import get_logger
from app.models import MarketData
from app.services.coingecko import CoinGeckoClient

logger = get_logger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()


async def ingest_market_data() -> None:
    logger.info("Starting market data ingestion")
    
    try:
        client = CoinGeckoClient()
        crypto_data = await client.fetch_top_cryptos(limit=10)
        
        with Session(engine) as db:
            try:
                for coin in crypto_data:
                    market_data = MarketData(
                        symbol=coin["symbol"].upper(),
                        price=coin["current_price"],
                        volume_24h=coin["total_volume"],
                        market_cap=coin["market_cap"],
                        timestamp=datetime.utcnow()
                    )
                    db.add(market_data)
                
                db.commit()
                logger.info(f"Stored {len(crypto_data)} market data records")
                
            except Exception as db_error:
                db.rollback()
                logger.error(f"Database error during ingestion: {db_error}", exc_info=True)
                raise
    
    except Exception as e:
        logger.error(f"Market data ingestion failed: {e}", exc_info=True)


def start_scheduler() -> None:
    scheduler.add_job(
        ingest_market_data,
        trigger=IntervalTrigger(minutes=settings.ingest_interval_minutes),
        id="ingest_market_data",
        name="Ingest crypto market data",
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    logger.info(f"Scheduler started - interval: {settings.ingest_interval_minutes} minutes")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")
