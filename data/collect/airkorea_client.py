import os
import requests
from typing import Optional

BASE_URL = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
API_KEY = os.getenv("AIR_KOREA_KEY")

# 수원대 인근 측정소: 봉담읍 인근 → 수원 측정소 사용
STATION_NAME = "수원"


def get_air_quality() -> Optional[dict]:
    """실시간 PM10, PM2.5, 통합대기환경지수"""
    try:
        res = requests.get(
            f"{BASE_URL}/getMsrstnAcctoRltmMesureDnsty",
            params={
                "serviceKey": API_KEY,
                "numOfRows": 1,
                "pageNo": 1,
                "stationName": STATION_NAME,
                "dataTerm": "DAILY",
                "ver": "1.3",
                "_returnType": "json",
            },
            timeout=10,
        )
        res.raise_for_status()
        items = res.json()["response"]["body"]["items"]
        if not items:
            return None
        item = items[0]
        return {
            "pm10": _safe_float(item.get("pm10Value")),
            "pm25": _safe_float(item.get("pm25Value")),
            "khai_grade": item.get("khaiGrade"),  # 1=좋음 2=보통 3=나쁨 4=매우나쁨
        }
    except Exception as e:
        print(f"[에어코리아] 오류: {e}")
        return None


def _safe_float(val) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
