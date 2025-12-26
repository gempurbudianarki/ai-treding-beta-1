from flask import Flask, render_template, jsonify, request
from pathlib import Path
import json
import time

app = Flask(__name__, template_folder="templates", static_folder="static")

STATUS_FILE = Path("data/status.json")
CONTROL_FILE = Path("data/control.json")
HISTORY_FILE = Path("data/history.json")


# ==========================================================
# UTIL
# ==========================================================
def load_json(path):
    if not Path(path).exists():
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except:
        return {}


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=4), encoding="utf-8")


# ==========================================================
# DASHBOARD PAGE
# ==========================================================
@app.route("/")
def dashboard():
    status = load_json(STATUS_FILE)
    control = load_json(CONTROL_FILE)
    return render_template("dashboard.html", status=status, control=control)


# ==========================================================
# API: get live status from bot
# ==========================================================
@app.route("/api/status")
def api_status():
    return jsonify(load_json(STATUS_FILE))


# ==========================================================
# API: toggle bot trading ON/OFF
# ==========================================================
@app.route("/api/toggle", methods=["POST"])
def api_toggle():
    ctl = load_json(CONTROL_FILE)
    body = request.json

    ctl["trading_enabled"] = body.get("trading_enabled", False)
    save_json(CONTROL_FILE, ctl)

    return jsonify({"success": True, "control": ctl})


# ==========================================================
# API: set MODE bot (SAFE / BALANCED / AGGRESSIVE / SCALPING_M5)
# ==========================================================
@app.route("/api/set_mode", methods=["POST"])
def api_set_mode():
    ctl = load_json(CONTROL_FILE)
    body = request.json

    mode = body.get("mode", "SAFE").upper()
    ctl["mode"] = mode

    save_json(CONTROL_FILE, ctl)

    return jsonify({"success": True, "control": ctl})


# ==========================================================
# API: signals history (from history.json)
# ==========================================================
@app.route("/api/signals")
def api_signals():
    data = load_json(HISTORY_FILE)
    return jsonify(data.get("signals", []))


# ==========================================================
# API: PnL chart data
# ==========================================================
@app.route("/api/pnl")
def api_pnl():
    data = load_json(HISTORY_FILE)
    return jsonify({
        "daily": data.get("daily_pnl", []),
        "weekly": data.get("weekly_pnl", [])
    })


# ==========================================================
# START SERVER
# ==========================================================
if __name__ == "__main__":
    print("Dashboard running: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
