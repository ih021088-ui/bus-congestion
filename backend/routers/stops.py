from fastapi import APIRouter, Query
from data.collect.tago_client import search_stops

router = APIRouter()

# 주요 도시코드 (TAGO 기준)
CITY_CODES = {
    "서울": 11,
    "부산": 21,
    "대구": 22,
    "인천": 12,
    "광주": 24,
    "대전": 25,
    "울산": 26,
    "경기": 31,
    "강원": 32,
    "충북": 33,
    "충남": 34,
    "전북": 35,
    "전남": 36,
    "경북": 37,
    "경남": 38,
    "제주": 39,
}


@router.get("/stops/search")
def search(
    name: str = Query(..., description="정류장 이름 (예: 수원대학교)"),
    city: str = Query(..., description="도시명 (예: 경기, 서울)"),
):
    """정류장 이름으로 검색 → nodeId, 좌표 반환"""
    city_code = CITY_CODES.get(city)
    if not city_code:
        return {"error": f"지원하지 않는 도시: {city}", "supported": list(CITY_CODES.keys())}

    results = search_stops(name, city_code)
    return {
        "city": city,
        "city_code": city_code,
        "results": [
            {
                "node_id": r.get("nodeid"),
                "name": r.get("nodenm"),
                "no": r.get("nodeno"),
            }
            for r in results
        ],
    }


@router.get("/stops/cities")
def get_cities():
    """지원 도시 목록"""
    return {"cities": list(CITY_CODES.keys())}
