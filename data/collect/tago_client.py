import os
import requests
from datetime import datetime
from typing import Optional

BASE_URL = "http://apis.data.go.kr/1613000"
API_KEY = os.getenv("DATA_GO_KR_KEY")

# 수원대 7790 정류장 TAGO 노드 ID
# 최초 1회: get_stop_node_id("수원대학교") 로 확인 후 여기에 기입
SUWON_UNIV_NODE_ID = "GGB234000743"  # 확인 필요 - 실제 노드ID로 교체
CITY_CODE = 31  # 경기도


def _get(service: str, operation: str, params: dict) -> Optional[dict]:
    url = f"{BASE_URL}/{service}/{operation}"
    params.update({
        "serviceKey": API_KEY,
        "numOfRows": 50,
        "pageNo": 1,
        "_type": "json",
    })
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        body = res.json().get("response", {}).get("body", {})
        return body
    except Exception as e:
        print(f"[TAGO] {service}/{operation} 오류: {e}")
        return None


def get_stop_node_id(stop_name: str) -> list[dict]:
    """정류장 이름으로 TAGO 노드ID 조회 - 최초 1회만 사용"""
    body = _get(
        "BusSttnInfoInqireService",
        "getSttnNoList",
        {"cityCode": CITY_CODE, "nodeNm": stop_name},
    )
    if not body:
        return []
    items = body.get("items", {}).get("item", [])
    return items if isinstance(items, list) else [items]


def get_arrivals(node_id: str = SUWON_UNIV_NODE_ID) -> list[dict]:
    """정류장 실시간 도착 예정 버스 목록"""
    body = _get(
        "ArvlInfoInqireService",
        "getSttnAcctoArvlPrearngeInfoList",
        {"cityCode": CITY_CODE, "nodeId": node_id},
    )
    if not body:
        return []
    items = body.get("items", {}).get("item", [])
    return items if isinstance(items, list) else [items]


def get_bus_location(route_id: str) -> list[dict]:
    """노선 실시간 버스 위치"""
    body = _get(
        "BusLcInfoInqireService",
        "getRouteAcctoBusLcList",
        {"cityCode": CITY_CODE, "routeId": route_id},
    )
    if not body:
        return []
    items = body.get("items", {}).get("item", [])
    return items if isinstance(items, list) else [items]


def get_routes_at_stop(node_id: str = SUWON_UNIV_NODE_ID) -> list[dict]:
    """정류장에 서는 노선 목록"""
    body = _get(
        "BusRouteInfoInqireService",
        "getSttnAcctoRouteList",
        {"cityCode": CITY_CODE, "nodeId": node_id},
    )
    if not body:
        return []
    items = body.get("items", {}).get("item", [])
    return items if isinstance(items, list) else [items]


def snapshot(node_id: str = SUWON_UNIV_NODE_ID) -> dict:
    """폴링 1회 - 현재 상태 요약"""
    arrivals = get_arrivals(node_id)
    now = datetime.now()

    buses_in_20min = sum(
        1 for a in arrivals if isinstance(a, dict) and int(a.get("arrtime", 9999)) <= 1200
    )
    intervals = [
        int(a["arrtime"]) for a in arrivals
        if isinstance(a, dict) and a.get("arrtime") and int(a["arrtime"]) > 0
    ]
    avg_interval = sum(intervals) / len(intervals) / 60 if intervals else None

    return {
        "ts": now.isoformat(),
        "stop_id": node_id,
        "buses_arriving_20min": buses_in_20min,
        "avg_interval_min": round(avg_interval, 1) if avg_interval else None,
        "raw_arrivals": arrivals,
    }
