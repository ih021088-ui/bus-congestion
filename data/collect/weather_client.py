import os
import requests
from datetime import datetime
from typing import Optional

BASE_URL = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService"
API_KEY = os.getenv("KMA_API_KEY")

# 수원대(화성시 봉담읍) 기상청 격자 좌표
# https://www.kma.go.kr/HELP/contentview.do?CONTENT_ID=45352002 에서 확인
NX, NY = 57, 119


def _base_date_time() -> tuple[str, str]:
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    # 단기예보 발표 시각: 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300
    issue_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    base_hour = max((h for h in issue_hours if h <= hour), default=23)
    if hour < 2:
        from datetime import timedelta
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
        return base_date, "2300"
    return now.strftime("%Y%m%d"), f"{base_hour:02d}00"


def get_forecast() -> Optional[dict]:
    """단기예보 - 향후 기온/강수/하늘상태"""
    base_date, base_time = _base_date_time()
    try:
        res = requests.get(
            f"{BASE_URL}/getVilageFcst",
            params={
                "authKey": API_KEY,
                "numOfRows": 100,
                "pageNo": 1,
                "dataType": "JSON",
                "base_date": base_date,
                "base_time": base_time,
                "nx": NX,
                "ny": NY,
            },
            timeout=10,
        )
        res.raise_for_status()
        items = res.json()["response"]["body"]["items"]["item"]
        return _parse_forecast(items)
    except Exception as e:
        print(f"[날씨] 단기예보 오류: {e}")
        return None


def get_current_weather() -> Optional[dict]:
    """초단기실황 - 현재 기온/강수"""
    now = datetime.now()
    try:
        res = requests.get(
            f"{BASE_URL}/getUltraSrtNcst",
            params={
                "authKey": API_KEY,
                "numOfRows": 10,
                "pageNo": 1,
                "dataType": "JSON",
                "base_date": now.strftime("%Y%m%d"),
                "base_time": f"{now.hour:02d}00",
                "nx": NX,
                "ny": NY,
            },
            timeout=10,
        )
        res.raise_for_status()
        items = res.json()["response"]["body"]["items"]["item"]
        return _parse_current(items)
    except Exception as e:
        print(f"[날씨] 초단기실황 오류: {e}")
        return None


def _parse_current(items: list) -> dict:
    data = {i["category"]: i["obsrValue"] for i in items}
    return {
        "temp": float(data.get("T1H", 0)),
        "precipitation": float(data.get("RN1", 0)),
        "is_raining": int(data.get("PTY", 0)) > 0,
        "humidity": float(data.get("REH", 0)),
        "wind_speed": float(data.get("WSD", 0)),
    }


def _parse_forecast(items: list) -> dict:
    """향후 3시간 예보만 추출"""
    now = datetime.now()
    target_hour = (now.hour + 1) % 24
    target_time = f"{target_hour:02d}00"

    data = {
        i["category"]: i["fcstValue"]
        for i in items
        if i.get("fcstTime") == target_time
    }
    return {
        "forecast_temp": float(data.get("TMP", 0)),
        "forecast_precipitation_prob": int(data.get("POP", 0)),
        "forecast_is_raining": int(data.get("PTY", 0)) > 0,
        "forecast_sky": int(data.get("SKY", 1)),
    }
