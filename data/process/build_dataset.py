"""
stcis.go.kr 재차인원 CSV → 학습용 데이터셋 변환

사용법:
  1. stcis.go.kr에서 7790번 노선 재차인원 CSV 다운로드
  2. data/raw/stcis_7790.csv 로 저장
  3. python -m data.process.build_dataset 실행
  → data/processed/merged.csv 생성
"""
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

STCIS_PATH = Path("data/raw/stcis_7790.csv")
OUT_PATH = Path("data/processed/merged.csv")

# 수원대입구 정류장 이름 (stcis 데이터 기준)
TARGET_STOP = "수원대입구"

# 버스 정원 70명 기준 혼잡도 임계값
CONGESTION_HIGH = 50   # 혼잡
CONGESTION_MID  = 20   # 보통 (20 미만 = 여유)


def load_stcis(path: Path) -> pd.DataFrame:
    """stcis CSV 로드 - 정류장명, 시간대별 재차인원"""
    df = pd.read_csv(path, encoding="utf-8-sig")
    return df


def extract_target_stop(df: pd.DataFrame, stop_name: str) -> pd.Series:
    """수원대입구 행만 추출"""
    mask = df.apply(lambda col: col.astype(str).str.contains(stop_name, na=False)).any(axis=1)
    rows = df[mask]
    if rows.empty:
        raise ValueError(f"'{stop_name}' 정류장을 찾을 수 없습니다. 컬럼명을 확인해주세요.")
    return rows.iloc[0]


def occupancy_to_label(occupancy: int) -> str:
    if occupancy >= CONGESTION_HIGH:
        return "혼잡"
    elif occupancy >= CONGESTION_MID:
        return "보통"
    return "여유"


def build_hourly_rows(stop_row: pd.Series) -> pd.DataFrame:
    """시간대별 재차인원 → 학습용 행 생성"""
    hours = list(range(4, 24)) + list(range(0, 4))  # 04~23, 00~03
    records = []

    for hour in hours:
        col = str(hour).zfill(2)
        if col not in stop_row.index:
            continue
        try:
            occupancy = int(stop_row[col])
        except (ValueError, TypeError):
            continue

        label = occupancy_to_label(occupancy)
        records.append({
            "hour": hour,
            "occupancy": occupancy,
            "congestion_label": label,
        })

    return pd.DataFrame(records)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """요일/주말 피처 추가 (시간대 기반 평균값으로 채움)"""
    # 실제 날짜 데이터가 없으므로 시간대만으로 피처 구성
    df["minute"] = 0
    df["day_of_week"] = 1        # 평일 기본값 (추후 실제 날짜로 교체)
    df["is_weekend"] = 0
    df["is_holiday"] = 0
    df["temp"] = 15.0            # 평균 기온 기본값
    df["precipitation"] = 0.0
    df["is_raining"] = 0
    df["pm10"] = 30.0
    df["buses_arriving_20min"] = 3
    df["avg_interval_min"] = 15.0
    return df


def main(stcis_path: str = str(STCIS_PATH), out_path: str = str(OUT_PATH)):
    print(f"stcis 데이터 로드: {stcis_path}")
    df_raw = load_stcis(Path(stcis_path))

    print(f"'{TARGET_STOP}' 정류장 추출 중...")
    stop_row = extract_target_stop(df_raw, TARGET_STOP)

    print("시간대별 레이블 생성 중...")
    df = build_hourly_rows(stop_row)
    df = add_time_features(df)

    label_counts = df["congestion_label"].value_counts()
    print(f"레이블 분포: {label_counts.to_dict()}")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {out_path} ({len(df)}행)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stcis", default=str(STCIS_PATH))
    parser.add_argument("--out", default=str(OUT_PATH))
    args = parser.parse_args()
    main(args.stcis, args.out)
