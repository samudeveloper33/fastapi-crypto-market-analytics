from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    symbol: str
    price_change_pct: float
    volume_change_pct: float
    momentum_score: float
    period_hours: int
    data_points: int
