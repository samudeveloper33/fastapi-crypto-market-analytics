from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, select

from app.core.database import get_db
from app.models import MarketData
from app.schemas import MarketDataResponse, PriceResponse

router = APIRouter(prefix="/markets", tags=["Market Data"])


@router.get("", response_model=List[MarketDataResponse])
def get_markets(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    latest_ts = db.exec(
        select(MarketData.timestamp).order_by(desc(MarketData.timestamp)).limit(1)
    ).first()
    
    if not latest_ts:
        return []
    
    results = db.exec(
        select(MarketData).where(MarketData.timestamp == latest_ts).limit(limit)
    ).all()
    
    return results


@router.get("/price", response_model=PriceResponse)
def get_price(
    symbol: str = Query(..., description="Cryptocurrency symbol (e.g., BTC)"),
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()
    
    result = db.exec(
        select(MarketData)
        .where(MarketData.symbol == symbol)
        .order_by(desc(MarketData.timestamp))
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbol: {symbol}"
        )
    
    return PriceResponse(
        symbol=result.symbol,
        price=result.price,
        timestamp=result.timestamp
    )


@router.get("/history", response_model=List[MarketDataResponse])
def get_history(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()
    
    results = db.exec(
        select(MarketData)
        .where(MarketData.symbol == symbol)
        .order_by(desc(MarketData.timestamp))
        .limit(limit)
    ).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for symbol: {symbol}"
        )
    
    return list(reversed(results))
