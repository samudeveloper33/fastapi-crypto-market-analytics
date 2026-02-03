from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlmodel import Session, select

from app.models import MarketData


class StrategyService:
    SHORT_WINDOW = 5
    LONG_WINDOW = 20
    BASE_CONFIDENCE = 0.5
    MAX_CONFIDENCE = 0.9
    
    def __init__(self, db: Session):
        self.db = db
    
    def run(self, symbol: str, lookback_hours: int = 48) -> Optional[dict]:
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        data = self.db.exec(
            select(MarketData)
            .where(MarketData.symbol == symbol, MarketData.timestamp >= cutoff)
            .order_by(MarketData.timestamp)
        ).all()
        
        if len(data) < self.LONG_WINDOW:
            return None
        
        df = pd.DataFrame([{"price": r.price, "timestamp": r.timestamp} for r in data])
        df["short_ma"] = df["price"].rolling(window=self.SHORT_WINDOW).mean()
        df["long_ma"] = df["price"].rolling(window=self.LONG_WINDOW).mean()
        
        if len(df) < 2:
            return None
        
        latest, previous = df.iloc[-1], df.iloc[-2]
        
        if pd.isna(latest["short_ma"]) or pd.isna(latest["long_ma"]):
            return None
        
        signal, reason, confidence = self._generate_signal(latest, previous)
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": round(confidence, 2),
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
    
    def _generate_signal(self, latest: pd.Series, previous: pd.Series) -> tuple[str, str, float]:
        short_ma, long_ma = latest["short_ma"], latest["long_ma"]
        prev_short, prev_long = previous["short_ma"], previous["long_ma"]
        
        if prev_short <= prev_long and short_ma > long_ma:
            separation = abs((short_ma - long_ma) / long_ma)
            confidence = min(self.MAX_CONFIDENCE, self.BASE_CONFIDENCE + 0.1 + separation * 10)
            return "BUY", "Short MA crossed above Long MA", confidence
        
        if prev_short >= prev_long and short_ma < long_ma:
            separation = abs((long_ma - short_ma) / long_ma)
            confidence = min(self.MAX_CONFIDENCE, self.BASE_CONFIDENCE + 0.1 + separation * 10)
            return "SELL", "Short MA crossed below Long MA", confidence
        
        if short_ma > long_ma:
            return "HOLD", "Bullish trend continues", self.BASE_CONFIDENCE
        
        return "HOLD", "Bearish trend continues", self.BASE_CONFIDENCE
