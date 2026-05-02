from pydantic import BaseModel
from typing import Optional


class CongestionResponse(BaseModel):
    stop_id: str
    ts: str
    label: str
    proba: dict[str, float]
    buses_arriving_20min: Optional[int]
    avg_interval_min: Optional[float]
    temp: Optional[float]
    is_raining: bool
    pm10: Optional[float]
    region: Optional[str]


class PredictionResponse(BaseModel):
    stop_id: str
    current: CongestionResponse
    forecast: list[dict]


class AlertConfig(BaseModel):
    threshold: str
    webhook_url: Optional[str] = None
