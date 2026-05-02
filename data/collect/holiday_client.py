import os
import requests
from datetime import date
from functools import lru_cache

BASE_URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
API_KEY = os.getenv("DATA_GO_KR_KEY")


@lru_cache(maxsize=12)
def get_holidays(year: int, month: int) -> set[str]:
    """해당 월 공휴일 날짜 집합 반환 (YYYY-MM-DD 형식)"""
    dates = set()
    for operation in ["getRestDeInfo", "getHoliDeInfo"]:
        try:
            res = requests.get(
                f"{BASE_URL}/{operation}",
                params={
                    "serviceKey": API_KEY,
                    "numOfRows": 30,
                    "pageNo": 1,
                    "solYear": year,
                    "solMonth": f"{month:02d}",
                    "_type": "json",
                },
                timeout=10,
            )
            res.raise_for_status()
            body = res.json()["response"]["body"]
            items = body.get("items", {})
            if not items:
                continue
            item_list = items.get("item", [])
            if isinstance(item_list, dict):
                item_list = [item_list]
            for item in item_list:
                locdate = str(item.get("locdate", ""))
                if len(locdate) == 8:
                    dates.add(f"{locdate[:4]}-{locdate[4:6]}-{locdate[6:]}")
        except Exception as e:
            print(f"[공휴일] {operation} 오류: {e}")
    return dates


def is_holiday(d: date) -> bool:
    holidays = get_holidays(d.year, d.month)
    return d.strftime("%Y-%m-%d") in holidays
