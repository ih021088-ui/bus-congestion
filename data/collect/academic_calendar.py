from datetime import date

# 수원대학교 2025-2026 학사일정 (홈페이지 확인 후 업데이트)
# https://www.suwon.ac.kr/index.html?menuno=727

SEMESTERS = [
    {
        "name": "2025-1학기",
        "start": date(2025, 3, 3),
        "end": date(2025, 6, 20),
        "midterm": (date(2025, 4, 21), date(2025, 4, 25)),
        "final": (date(2025, 6, 9), date(2025, 6, 13)),
    },
    {
        "name": "2025-2학기",
        "start": date(2025, 9, 1),
        "end": date(2025, 12, 19),
        "midterm": (date(2025, 10, 20), date(2025, 10, 24)),
        "final": (date(2025, 12, 8), date(2025, 12, 12)),
    },
    {
        "name": "2026-1학기",
        "start": date(2026, 3, 2),
        "end": date(2026, 6, 19),
        "midterm": (date(2026, 4, 20), date(2026, 4, 24)),
        "final": (date(2026, 6, 8), date(2026, 6, 12)),
    },
]

# 수업 시작 시간 (정시 기준) - 버스 정류장 혼잡 예상 시각
CLASS_START_HOURS = {9, 10, 11, 12, 13, 14, 15, 16, 17, 18}
CLASS_END_HOURS = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}


def get_semester_info(d: date) -> dict:
    for sem in SEMESTERS:
        if sem["start"] <= d <= sem["end"]:
            mid_s, mid_e = sem["midterm"]
            fin_s, fin_e = sem["final"]
            return {
                "is_semester": True,
                "is_exam": (mid_s <= d <= mid_e) or (fin_s <= d <= fin_e),
                "semester_name": sem["name"],
            }
    return {"is_semester": False, "is_exam": False, "semester_name": None}


def is_class_start_soon(hour: int, minute: int) -> bool:
    """수업 시작 30분 전 ~ 시작 직후 (혼잡 예상)"""
    if hour in CLASS_START_HOURS and minute >= 30:
        return True
    if (hour + 1) in CLASS_START_HOURS and minute <= 10:
        return True
    return False


def is_class_end_soon(hour: int, minute: int) -> bool:
    """수업 종료 전후 (혼잡 예상)"""
    if hour in CLASS_END_HOURS and 45 <= minute <= 59:
        return True
    if (hour + 1) in CLASS_END_HOURS and minute <= 15:
        return True
    return False
