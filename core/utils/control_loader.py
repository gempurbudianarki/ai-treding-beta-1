import json
from pathlib import Path

CONTROL_FILE = Path("data/control.json")

def load_control():
    if not CONTROL_FILE.exists():
        return {
            "trading_enabled": True,
            "mode": "SAFE"
        }

    try:
        data = json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
        return {
            "trading_enabled": data.get("trading_enabled", True),
            "mode": data.get("mode", "SAFE")
        }
    except:
        return {
            "trading_enabled": True,
            "mode": "SAFE"
        }
