from fastapi import APIRouter
from backend.schema import AlertConfig

router = APIRouter()

_alert_config: AlertConfig = AlertConfig(threshold="혼잡")


@router.get("/alert/config")
def get_alert_config():
    return _alert_config


@router.post("/alert/config")
def set_alert_config(config: AlertConfig):
    global _alert_config
    _alert_config = config
    return {"status": "ok", "config": _alert_config}


@router.get("/alert/check")
def check_alert(label: str):
    """현재 혼잡도 레이블이 임계값 이상이면 알림 여부 반환"""
    level_map = {"여유": 0, "보통": 1, "혼잡": 2}
    current_level = level_map.get(label, 0)
    threshold_level = level_map.get(_alert_config.threshold, 2)
    should_alert = current_level >= threshold_level
    return {"should_alert": should_alert, "label": label, "threshold": _alert_config.threshold}
