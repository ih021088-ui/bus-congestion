from fastapi import APIRouter, Query
from datetime import datetime, date

from data.collect.tago_client import snapshot as tago_snapshot
from data.collect.weather_client import get_current_weather
from data.collect.airkorea_client import get_air_quality
from data.collect.holiday_client import is_holiday
from model.predict import predict_with_proba, predict_future

router = APIRouter()


@router.get("/predict")
def get_prediction(
    stop_id: str = Query(..., description="TAGO 정류장 노드ID"),
    city_code: int = Query(..., description="TAGO 도시코드"),
    region: str = Query("서울", description="날씨/대기질 조회 지역명"),
):
    now = datetime.now()
    today = date.today()

    tago = tago_snapshot(stop_id, city_code)
    weather = get_current_weather(region) or {}
    air = get_air_quality(region) or {}

    base_row = {
        "ts": now.isoformat(),
        **tago,
        **weather,
        **air,
        "is_holiday": int(is_holiday(today)),
    }

    current = predict_with_proba(base_row) or {"label": "알 수 없음", "proba": {}}
    forecast = predict_future(base_row, horizon_minutes=[30, 60])

    return {
        "stop_id": stop_id,
        "current": {**current, "ts": now.isoformat()},
        "forecast": forecast,
    }
