"""
옵션 A: 규칙 기반 임시 모델
실행: python -m model.bootstrap_A_rule
"""
import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path("model/saved/lgbm_model.pkl")


class RuleBasedModel:
    """buses_arriving_20min + hour 기반 규칙 분류기 (sklearn 호환)"""

    def predict(self, X):
        results = []
        for _, row in X.iterrows():
            buses = row.get("buses_arriving_20min", 0)
            hour = row.get("hour", 12)
            is_rush = hour in range(7, 10) or hour in range(17, 20)

            if buses >= 15 or (buses >= 10 and is_rush):
                results.append(2)  # 혼잡
            elif buses >= 7 or (buses >= 4 and is_rush):
                results.append(1)  # 보통
            else:
                results.append(0)  # 여유
        return np.array(results)

    def predict_proba(self, X):
        preds = self.predict(X)
        proba_map = {
            0: [0.80, 0.15, 0.05],
            1: [0.15, 0.70, 0.15],
            2: [0.05, 0.15, 0.80],
        }
        return np.array([proba_map[p] for p in preds])


if __name__ == "__main__":
    MODEL_PATH.parent.mkdir(exist_ok=True)
    model = RuleBasedModel()
    joblib.dump(model, MODEL_PATH)
    print(f"[옵션 A] 규칙 기반 모델 저장 완료: {MODEL_PATH}")
