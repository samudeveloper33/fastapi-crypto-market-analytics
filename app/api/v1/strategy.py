from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.database import get_db
from app.schemas import StrategySignal
from app.services.strategy import StrategyService

router = APIRouter(prefix="/strategy", tags=["Strategy"])


@router.post("/run", response_model=StrategySignal)
def run_strategy(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    lookback_hours: int = Query(default=48, ge=24, le=168, description="Lookback period"),
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()
    service = StrategyService(db)
    result = service.run(symbol, lookback_hours)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Insufficient data for {symbol}"
        )
    
    return result
