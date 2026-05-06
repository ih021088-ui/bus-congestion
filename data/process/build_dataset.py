"""
SQLite DB → 학습용 CSV 변환
실행: python -m data.process.build_dataset
옵션: --db bus_congestion.db --out data/processed/merged.csv --min-rows 100
"""
import argparse
import sqlite3
import pandas as pd
from pathlib import Path

from model.features import passenger_count_to_label

DEFAULT_DB = "bus_congestion.db"
DEFAULT_OUT = "data/processed/merged.csv"


def load_snapshots(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM snapshots ORDER BY ts", conn)
    conn.close()
    return df


def build(db_path: str, out_path: str, min_rows: int = 0):
    print(f"DB 로드 중: {db_path}")
    df = load_snapshots(db_path)
    print(f"  총 {len(df)}개 레코드")

    if len(df) < min_rows:
        print(f"  데이터 부족 (최소 {min_rows}개 필요) → 중단")
        return

    df["ts"] = pd.to_datetime(df["ts"])
    df["minute"] = df["ts"].dt.minute

    # congestion_actual이 있으면 우선 사용, 없으면 buses_arriving_20min으로 생성
    if df["congestion_actual"].notna().sum() > 0:
        df["congestion_label"] = df["congestion_actual"]
        df = df[df["congestion_label"].notna()]
        print(f"  congestion_actual 사용: {len(df)}개")
    else:
        df = df[df["buses_arriving_20min"].notna()]
        df["congestion_label"] = df["buses_arriving_20min"].astype(int).apply(passenger_count_to_label)
        print(f"  buses_arriving_20min → 레이블 변환: {len(df)}개")

    print(f"\n레이블 분포:\n{df['congestion_label'].value_counts().to_string()}")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n저장 완료: {out} ({len(df)}행)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--min-rows", type=int, default=0, help="최소 레코드 수 (미달 시 중단)")
    args = parser.parse_args()
    build(args.db, args.out, args.min_rows)
