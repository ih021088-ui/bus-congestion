"""
옵션 B: 합성 데이터(synthetic data) 생성 후 LightGBM 학습
실행: python -m model.bootstrap_B_synthetic
"""
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from model.features import FEATURE_COLS, LABEL_MAP

MODEL_PATH = Path("model/saved/lgbm_model.pkl")
N_SAMPLES = 20000
RANDOM_STATE = 42


def generate_synthetic_data(n: int) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)

    hour        = rng.integers(0, 24, n)
    minute      = rng.integers(0, 60, n)
    day_of_week = rng.integers(0, 7, n)
    is_weekend  = (day_of_week >= 5).astype(int)
    is_holiday  = rng.binomial(1, 0.05, n)
    temp        = rng.normal(15, 10, n).clip(-15, 40)
    is_raining  = rng.binomial(1, 0.2, n)
    precipitation = is_raining * rng.exponential(3, n)
    pm10        = rng.gamma(3, 15, n).clip(5, 200)

    # 버스 수: 출퇴근 시간대 + 평일에 많아지는 패턴 반영
    is_rush = ((hour >= 7) & (hour < 10)) | ((hour >= 17) & (hour < 20))
    is_late_night = (hour >= 23) | (hour < 6)

    base_buses = rng.poisson(8, n).astype(float)
    base_buses += is_rush * rng.poisson(8, n)
    base_buses -= is_weekend * rng.poisson(3, n)
    base_buses -= is_holiday * rng.poisson(3, n)
    base_buses -= is_late_night * rng.poisson(4, n)
    base_buses += is_raining * rng.poisson(2, n)  # 비 오면 버스 이용 증가
    buses_arriving_20min = base_buses.clip(0, 30).astype(int)

    avg_interval_min = (30 / (buses_arriving_20min + 1) + rng.normal(0, 1, n)).clip(2, 40)

    # 레이블: buses_arriving_20min 기준 (features.py의 THRESHOLDS와 동일)
    label = np.where(buses_arriving_20min >= 15, 2,
            np.where(buses_arriving_20min >= 7,  1, 0))

    return pd.DataFrame({
        "hour": hour, "minute": minute,
        "day_of_week": day_of_week, "is_weekend": is_weekend,
        "is_holiday": is_holiday, "temp": temp,
        "precipitation": precipitation, "is_raining": is_raining,
        "pm10": pm10, "buses_arriving_20min": buses_arriving_20min,
        "avg_interval_min": avg_interval_min,
        "label": label,
    })


if __name__ == "__main__":
    print(f"합성 데이터 {N_SAMPLES}건 생성 중...")
    df = generate_synthetic_data(N_SAMPLES)

    label_counts = df["label"].value_counts().sort_index()
    print(f"레이블 분포: 여유={label_counts.get(0,0)}, 보통={label_counts.get(1,0)}, 혼잡={label_counts.get(2,0)}")

    X = df[FEATURE_COLS]
    y = df["label"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    model = lgb.LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        verbose=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(30, verbose=False)])

    preds = model.predict(X_val)
    print("\n--- 검증 성능 ---")
    print(classification_report(y_val, preds, target_names=["여유", "보통", "혼잡"]))

    importance = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print("피처 중요도:")
    print(importance.to_string())

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n[옵션 B] LightGBM 모델 저장 완료: {MODEL_PATH}")
