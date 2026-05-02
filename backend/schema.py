from pydantic import BaseModel
from typing import Optional


class CongestionResponse(BaseModel):
    stop_id: str
    ts: str
    label: str                     # 혼잡 / 보통 / 여유
    proba: dict[str, float]
    buses_arriving_20min: Optional[int]
    avg_interval_min: Optional[float]
    temp: Optional[float]
    is_raining: bool
    pm10: Optional[float]
    is_semester: bool
    is_exam: bool


class PredictionResponse(BaseModel):
    stop_id: str
    current: CongestionResponse
    forecast: list[dict]           # 30분, 60분 후 예측


class AlertConfig(BaseModel):
    threshold: str                 # 혼잡 / 보통
    webhook_url: Optional[str] = None
