from fastapi import APIRouter, Query
from datetime import datetime, date

from data.collect.tago_client import snapshot as tago_snapshot
from data.collect.weather_client import get_current_weather
from data.collect.airkorea_client import get_air_quality
from data.collect.holiday_client import is_holiday
from data.collect.academic_calendar import get_semester_info
from model.predict import predict_with_proba, predict_future

router = APIRouter()


@router.get("/predict")
def get_prediction(
    stop_id: str = Query(..., description="TAGO 정류장 노드ID"),
    city_code: int = Query(..., description="TAGO 도시코드"),
    region: str = Query("서울", description="날씨/대기질 조회 지역명"),
    is_univ_area: bool = Query(False, description="대학교 인근 정류장 여부"),
):
    """현재 + 향후 30/60분 후 혼잡도 예측"""
    now = datetime.now()
    today = date.today()

    tago = tago_snapshot(stop_id, city_code)
    weather = get_current_weather(region) or {}
    air = get_air_quality(region) or {}

    sem = get_semester_info(today) if is_univ_area else {"is_semester": False, "is_exam": False}

    base_row = {
        "ts": now.isoformat(),
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
        "stop_id": stop_id,
        "current": {**current, "ts": now.isoformat()},
        "forecast": forecast,
    }
