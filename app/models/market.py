from datetime import datetime
from typing import Optional

from sqlmodel import Field, Index, SQLModel


class MarketData(SQLModel, table=True):
    __tablename__ = "market_data"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    price: float
    volume_24h: float
    market_cap: float
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    __table_args__ = (Index("idx_symbol_timestamp", "symbol", "timestamp"),)
