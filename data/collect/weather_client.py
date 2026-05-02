import os
import requests
from datetime import datetime, timedelta
from typing import Optional

BASE_URL = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService"
API_KEY = os.getenv("KMA_API_KEY")

# 주요 지역 기상청 격자 좌표 (nx, ny)
# https://www.kma.go.kr 격자 변환 도구 참고
REGION_GRID: dict[str, tuple[int, int]] = {
    "서울":     (60, 127),
    "강남":     (61, 126),
    "강북":     (61, 128),
    "인천":     (55, 124),
    "수원":     (60, 121),
    "화성":     (57, 119),   # 수원대학교(봉담읍)
    "성남":     (63, 124),
    "용인":     (64, 119),
    "안양":     (59, 123),
    "부천":     (56, 125),
    "고양":     (57, 128),
    "의정부":   (61, 130),
    "부산":     (98, 76),
    "대구":     (89, 90),
    "광주":     (58, 74),
    "대전":     (67, 100),
    "울산":     (102, 84),
}

DEFAULT_GRID = (60, 127)  # 서울 기본값


def get_grid(region: str) -> tuple[int, int]:
    for key, grid in REGION_GRID.items():
        if key in region:
            return grid
    return DEFAULT_GRID


def _base_date_time() -> tuple[str, str]:
    now = datetime.now()
    hour = now.hour
    issue_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    base_hour = max((h for h in issue_hours if h <= hour), default=23)
    if hour < 2:
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
        return base_date, "2300"
    return now.strftime("%Y%m%d"), f"{base_hour:02d}00"


def get_forecast(region: str = "서울") -> Optional[dict]:
    """단기예보 - 향후 기온/강수/하늘상태"""
    nx, ny = get_grid(region)
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
                "nx": nx,
                "ny": ny,
            },
            timeout=10,
        )
        res.raise_for_status()
        items = res.json()["response"]["body"]["items"]["item"]
        return _parse_forecast(items)
    except Exception as e:
        print(f"[날씨] 단기예보 오류: {e}")
        return None


def get_current_weather(region: str = "서울") -> Optional[dict]:
    """초단기실황 - 현재 기온/강수"""
    nx, ny = get_grid(region)
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
                "nx": nx,
                "ny": ny,
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
