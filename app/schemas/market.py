from datetime import datetime

from pydantic import BaseModel


class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    volume_24h: float
    market_cap: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
