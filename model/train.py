"""
학습 실행: python -m model.train --data data/processed/merged.csv
"""
import argparse
import joblib
import pandas as pd
import lightgbm as lgb
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from model.features import build_features_from_df, FEATURE_COLS, LABEL_MAP, passenger_count_to_label

MODEL_PATH = Path("model/saved/lgbm_model.pkl")


def train(data_path: str):
    df = pd.read_csv(data_path)

    # 레이블 생성 (passenger_count 컬럼이 있는 경우)
    if "congestion_label" not in df.columns:
        df["congestion_label"] = df["passenger_count"].apply(passenger_count_to_label)

    df["label_enc"] = df["congestion_label"].map(LABEL_MAP)
    df = df.dropna(subset=["label_enc"])

    X = build_features_from_df(df)
    y = df["label_enc"].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
    )

    preds = model.predict(X_val)
    print(classification_report(y_val, preds, target_names=["여유", "보통", "혼잡"]))

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"모델 저장 완료: {MODEL_PATH}")

    # 피처 중요도 출력
    importance = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print("\n피처 중요도:")
    print(importance)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="학습 데이터 CSV 경로")
    args = parser.parse_args()
    train(args.data)
