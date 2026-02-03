from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from sqlmodel import Session, select

from app.models import MarketData


class AnalyticsService:
    MIN_DATA_POINTS = 2
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate(self, symbol: str, hours: int = 24) -> Optional[dict]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        data = self.db.exec(
            select(MarketData)
            .where(MarketData.symbol == symbol, MarketData.timestamp >= cutoff)
            .order_by(MarketData.timestamp)
        ).all()
        
        if len(data) < self.MIN_DATA_POINTS:
            return None
        
        df = pd.DataFrame([{
            "price": r.price,
            "volume_24h": r.volume_24h,
            "timestamp": r.timestamp
        } for r in data])
        
        return {
            "symbol": symbol,
            "price_change_pct": round(self._calculate_change(df["price"]), 2),
            "volume_change_pct": round(self._calculate_change(df["volume_24h"]), 2),
            "momentum_score": round(self._calculate_momentum(df), 4),
            "period_hours": hours,
            "data_points": len(data)
        }
    
    def _calculate_change(self, series: pd.Series) -> float:
        first, last = series.iloc[0], series.iloc[-1]
        return ((last - first) / first) * 100
    
    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        time_deltas = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
        
        if time_deltas.iloc[-1] == 0:
            return 0.0
        
        slope = np.polyfit(time_deltas, df["price"], 1)[0]
        return (slope / df["price"].mean()) * 100
