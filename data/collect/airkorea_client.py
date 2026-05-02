import os
import requests
from typing import Optional

BASE_URL = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
API_KEY = os.getenv("AIR_KOREA_KEY")

# 주요 지역 에어코리아 측정소 매핑
REGION_STATION: dict[str, str] = {
    "서울":   "중구",
    "강남":   "강남구",
    "강북":   "도봉구",
    "인천":   "인천",
    "수원":   "수원",
    "화성":   "수원",    # 수원대학교(봉담읍) 인근
    "성남":   "성남",
    "용인":   "용인",
    "안양":   "안양",
    "부천":   "부천",
    "고양":   "고양",
    "부산":   "부산",
    "대구":   "대구",
    "광주":   "광주",
    "대전":   "대전",
    "울산":   "울산",
}

DEFAULT_STATION = "중구"


def get_station(region: str) -> str:
    for key, station in REGION_STATION.items():
        if key in region:
            return station
    return DEFAULT_STATION


def get_air_quality(region: str = "서울") -> Optional[dict]:
    """실시간 PM10, PM2.5"""
    station = get_station(region)
    try:
        res = requests.get(
            f"{BASE_URL}/getMsrstnAcctoRltmMesureDnsty",
            params={
                "serviceKey": API_KEY,
                "numOfRows": 1,
                "pageNo": 1,
                "stationName": station,
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
            "khai_grade": item.get("khaiGrade"),
        }
    except Exception as e:
        print(f"[에어코리아] 오류: {e}")
        return None


def _safe_float(val) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
