import os
import re
import requests
from datetime import datetime
from typing import Optional
from xml.etree import ElementTree as ET

BASE_URL = "http://ws.bus.go.kr/api/rest"
API_KEY = os.getenv("DATA_GO_KR_KEY")


def _get(endpoint: str, params: dict) -> Optional[ET.Element]:
    params["serviceKey"] = API_KEY
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        res.raise_for_status()
        root = ET.fromstring(res.text)
        if root.findtext(".//headerCd") != "0":
            print(f"[서울버스] 오류: {root.findtext('.//headerMsg')}")
            return None
        return root
    except Exception as e:
        print(f"[서울버스] {endpoint} 오류: {e}")
        return None


def search_stops(stop_name: str) -> list[dict]:
    root = _get("stationinfo/getStationByName", {"stSrch": stop_name})
    if root is None:
        return []
    return [
        {
            "stId": item.findtext("stId"),
            "arsId": item.findtext("arsId"),
            "stNm": item.findtext("stNm"),
        }
        for item in root.findall(".//itemList")
    ]


def get_arrivals(ars_id: str) -> list[dict]:
    root = _get("stationinfo/getStationByUid", {"arsId": ars_id})
    if root is None:
        return []
    return [
        {
            "busRouteAbrv": item.findtext("busRouteAbrv"),
            "arrmsg1": item.findtext("arrmsg1"),
            "arrmsg2": item.findtext("arrmsg2"),
        }
        for item in root.findall(".//itemList")
    ]


def _parse_min(msg: str) -> Optional[int]:
    if not msg:
        return None
    if "곧" in msg or "도착" in msg:
        return 0
    m = re.search(r"(\d+)분", msg)
    return int(m.group(1)) if m else None


def snapshot(ars_id: str, region: str) -> dict:
    arrivals = get_arrivals(ars_id)
    now = datetime.now()

    mins = []
    for a in arrivals:
        for msg in [a.get("arrmsg1"), a.get("arrmsg2")]:
            v = _parse_min(msg)
            if v is not None:
                mins.append(v)

    buses_in_20min = sum(1 for m in mins if m <= 20)
    avg_interval = sum(mins) / len(mins) if mins else None

    return {
        "ts": now.isoformat(),
        "stop_id": ars_id,
        "city_code": 11,
        "buses_arriving_20min": buses_in_20min,
        "avg_interval_min": round(avg_interval, 1) if avg_interval else None,
        "raw_arrivals": arrivals,
    }
