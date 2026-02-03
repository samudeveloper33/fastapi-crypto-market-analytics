from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.database import get_db
from app.schemas import AnalyticsResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    hours: int = Query(default=24, ge=1, le=168, description="Lookback period in hours"),
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()
    service = AnalyticsService(db)
    result = service.calculate(symbol, hours)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Insufficient data for {symbol}"
        )
    
    return result
