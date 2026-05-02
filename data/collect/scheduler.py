"""
5분마다 폴링 → SQLite 저장
실행: python -m data.collect.scheduler
"""
import sqlite3
import time
from datetime import datetime, date

from data.collect.tago_client import snapshot as tago_snapshot
from data.collect.weather_client import get_current_weather
from data.collect.airkorea_client import get_air_quality
from data.collect.holiday_client import is_holiday
from data.collect.academic_calendar import get_semester_info
from model.predict import predict_congestion

DB_PATH = "bus_congestion.db"
POLL_INTERVAL = 300  # 5분


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            stop_id TEXT NOT NULL,
            buses_arriving_20min INTEGER,
            avg_interval_min REAL,
            temp REAL,
            precipitation REAL,
            is_raining INTEGER,
            pm10 REAL,
            pm25 REAL,
            hour INTEGER,
            day_of_week INTEGER,
            is_weekend INTEGER,
            is_holiday INTEGER,
            is_semester INTEGER,
            is_exam INTEGER,
            congestion_pred TEXT,
            congestion_actual TEXT
        )
    """)
    conn.commit()
    conn.close()


def collect_and_save():
    now = datetime.now()
    today = date.today()

    tago = tago_snapshot()
    weather = get_current_weather() or {}
    air = get_air_quality() or {}
    sem = get_semester_info(today)

    row = {
        "ts": now.isoformat(),
        "stop_id": tago["stop_id"],
        "buses_arriving_20min": tago.get("buses_arriving_20min"),
        "avg_interval_min": tago.get("avg_interval_min"),
        "temp": weather.get("temp"),
        "precipitation": weather.get("precipitation"),
        "is_raining": int(weather.get("is_raining", False)),
        "pm10": air.get("pm10"),
        "pm25": air.get("pm25"),
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "is_weekend": int(now.weekday() >= 5),
        "is_holiday": int(is_holiday(today)),
        "is_semester": int(sem["is_semester"]),
        "is_exam": int(sem["is_exam"]),
        "congestion_pred": predict_congestion(row) if predict_congestion else None,
    }

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO snapshots
        (ts, stop_id, buses_arriving_20min, avg_interval_min, temp, precipitation,
         is_raining, pm10, pm25, hour, day_of_week, is_weekend, is_holiday,
         is_semester, is_exam, congestion_pred)
        VALUES
        (:ts, :stop_id, :buses_arriving_20min, :avg_interval_min, :temp, :precipitation,
         :is_raining, :pm10, :pm25, :hour, :day_of_week, :is_weekend, :is_holiday,
         :is_semester, :is_exam, :congestion_pred)
    """, row)
    conn.commit()
    conn.close()
    print(f"[{now.strftime('%H:%M')}] 수집 완료 → 예측: {row['congestion_pred']}")


if __name__ == "__main__":
    init_db()
    print("폴링 시작 (5분 간격)")
    while True:
        try:
            collect_and_save()
        except Exception as e:
            print(f"[오류] {e}")
        time.sleep(POLL_INTERVAL)
