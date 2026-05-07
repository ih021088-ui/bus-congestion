import pandas as pd
from datetime import date

from data.collect.holiday_client import is_holiday

FEATURE_COLS = [
    "hour", "minute", "day_of_week", "is_weekend", "is_holiday",
    "temp", "precipitation", "is_raining", "pm10",
    "buses_arriving_20min", "avg_interval_min",
]

LABEL_MAP = {"여유": 0, "보통": 1, "혼잡": 2}
LABEL_INV = {v: k for k, v in LABEL_MAP.items()}

# 재차인원 기준 (버스 정원 70명)
THRESHOLDS = {"혼잡": 50, "보통": 20}


def passenger_count_to_label(count: int) -> str:
    if count >= THRESHOLDS["혼잡"]:
        return "혼잡"
    elif count >= THRESHOLDS["보통"]:
        return "보통"
    return "여유"


def build_features_from_row(row: dict) -> dict:
    from datetime import datetime
    ts = datetime.fromisoformat(row["ts"]) if isinstance(row.get("ts"), str) else datetime.now()
    today = ts.date()

    return {
        "hour": ts.hour,
        "minute": ts.minute,
        "day_of_week": ts.weekday(),
        "is_weekend": int(ts.weekday() >= 5),
        "is_holiday": int(is_holiday(today)),
        "temp": row.get("temp") or 15.0,
        "precipitation": row.get("precipitation") or 0.0,
        "is_raining": int(row.get("is_raining") or 0),
        "pm10": row.get("pm10") or 30.0,
        "buses_arriving_20min": row.get("buses_arriving_20min") or 0,
        "avg_interval_min": row.get("avg_interval_min") or 15.0,
    }


def build_features_from_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ts"] = pd.to_datetime(df["ts"])
    df["hour"] = df["ts"].dt.hour
    df["minute"] = df["ts"].dt.minute
    df["day_of_week"] = df["ts"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_holiday"] = df["ts"].dt.date.apply(is_holiday).astype(int)

    for col in ["temp", "precipitation", "is_raining", "pm10", "buses_arriving_20min", "avg_interval_min"]:
        if col not in df.columns:
            df[col] = 0

    return df[FEATURE_COLS]
