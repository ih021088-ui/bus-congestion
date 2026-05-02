from fastapi import APIRouter
from datetime import datetime, date

from data.collect.tago_client import snapshot as tago_snapshot
from data.collect.weather_client import get_current_weather, get_forecast
from data.collect.airkorea_client import get_air_quality
from data.collect.holiday_client import is_holiday
from data.collect.academic_calendar import get_semester_info
from model.predict import predict_with_proba, predict_future

router = APIRouter()


@router.get("/predict")
def get_prediction(horizon: int = 30):
    """현재 + 향후 혼잡도 예측 (horizon: 30 또는 60분)"""
    now = datetime.now()
    today = date.today()

    tago = tago_snapshot()
    weather = get_current_weather() or {}
    air = get_air_quality() or {}
    sem = get_semester_info(today)

    base_row = {
        "ts": now.isoformat(),
        "stop_id": tago["stop_id"],
        **tago,
        **weather,
        **air,
        "is_holiday": int(is_holiday(today)),
        "is_semester": int(sem["is_semester"]),
        "is_exam": int(sem["is_exam"]),
    }

    current = predict_with_proba(base_row) or {"label": "알 수 없음", "proba": {}}
    forecast = predict_future(base_row, horizon_minutes=[30, 60])

    return {
        "stop_id": tago["stop_id"],
        "current": {**current, "ts": now.isoformat()},
        "forecast": forecast,
    }
