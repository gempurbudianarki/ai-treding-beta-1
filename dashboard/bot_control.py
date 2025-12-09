from typing import Dict, Any
from .status_loader import save_control, load_control


def set_trading_enabled(enabled: bool) -> Dict[str, Any]:
    return save_control(trading_enabled=enabled)


def set_mode(mode: str) -> Dict[str, Any]:
    return save_control(mode=mode)


def get_control_state() -> Dict[str, Any]:
    return load_control()
