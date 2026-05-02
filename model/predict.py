import joblib
import pandas as pd
from pathlib import Path
from typing import Optional

from model.features import build_features_from_row, FEATURE_COLS, LABEL_INV

MODEL_PATH = Path("model/saved/lgbm_model.pkl")
_model = None


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_congestion(row: dict) -> Optional[str]:
    """단일 row 딕셔너리 → '혼잡' / '보통' / '여유'"""
    model = _load_model()
    if model is None:
        return None

    features = build_features_from_row(row)
    X = pd.DataFrame([features])[FEATURE_COLS]
    pred = model.predict(X)[0]
    return LABEL_INV[int(pred)]


def predict_with_proba(row: dict) -> Optional[dict]:
    """예측 결과 + 각 클래스 확률 반환"""
    model = _load_model()
    if model is None:
        return None

    features = build_features_from_row(row)
    X = pd.DataFrame([features])[FEATURE_COLS]
    proba = model.predict_proba(X)[0]
    pred = int(model.predict(X)[0])

    return {
        "label": LABEL_INV[pred],
        "proba": {
            "여유": round(float(proba[0]), 3),
            "보통": round(float(proba[1]), 3),
            "혼잡": round(float(proba[2]), 3),
        },
    }


def predict_future(base_row: dict, horizon_minutes: list[int] = [30, 60]) -> list[dict]:
    """향후 N분 후 혼잡도 예측"""
    from datetime import datetime, timedelta
    results = []
    base_ts = datetime.fromisoformat(base_row.get("ts", datetime.now().isoformat()))

    for minutes in horizon_minutes:
        future_row = base_row.copy()
        future_ts = base_ts + timedelta(minutes=minutes)
        future_row["ts"] = future_ts.isoformat()
        result = predict_with_proba(future_row)
        if result:
            result["minutes_ahead"] = minutes
            result["forecast_ts"] = future_ts.strftime("%H:%M")
            results.append(result)

    return results
