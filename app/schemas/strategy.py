from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class StrategySignal(BaseModel):
    symbol: str
    signal: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    timestamp: datetime
    
    @field_validator("signal")
    @classmethod
    def validate_signal(cls, v: str) -> str:
        allowed = {"BUY", "SELL", "HOLD"}
        if v not in allowed:
            raise ValueError(f"Signal must be one of {allowed}")
        return v
