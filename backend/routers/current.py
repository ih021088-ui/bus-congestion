from fastapi import APIRouter
from datetime import datetime, date

from data.collect.tago_client import snapshot as tago_snapshot
from data.collect.weather_client import get_current_weather
from data.collect.airkorea_client import get_air_quality
from data.collect.holiday_client import is_holiday
from data.collect.academic_calendar import get_semester_info
from model.predict import predict_with_proba

router = APIRouter()


@router.get("/current")
def get_current():
    """현재 정류장 혼잡도"""
    now = datetime.now()
    today = date.today()

    tago = tago_snapshot()
    weather = get_current_weather() or {}
    air = get_air_quality() or {}
    sem = get_semester_info(today)

    row = {
        "ts": now.isoformat(),
        "stop_id": tago["stop_id"],
        **tago,
        **weather,
        **air,
        "is_holiday": int(is_holiday(today)),
        "is_semester": int(sem["is_semester"]),
        "is_exam": int(sem["is_exam"]),
    }

    result = predict_with_proba(row) or {"label": "알 수 없음", "proba": {}}

    return {
        "stop_id": tago["stop_id"],
        "ts": now.isoformat(),
        "label": result["label"],
        "proba": result.get("proba", {}),
        "buses_arriving_20min": tago.get("buses_arriving_20min"),
        "avg_interval_min": tago.get("avg_interval_min"),
        "temp": weather.get("temp"),
        "is_raining": bool(weather.get("is_raining", False)),
        "pm10": air.get("pm10"),
        "is_semester": sem["is_semester"],
        "is_exam": sem["is_exam"],
    }
