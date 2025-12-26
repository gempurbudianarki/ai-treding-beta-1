from flask import Blueprint, render_template, jsonify, request
from .status_loader import load_status, load_control, save_control, load_history
from .bot_control import set_trading_enabled, set_mode

dash_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


@dash_bp.route("/")
def dashboard():
    status = load_status()
    control = load_control()
    history = load_history()
    return render_template(
        "dashboard.html",
        status=status,
        control=control,
        history=history,
    )


@dash_bp.route("/api/status")
def api_status():
    status = load_status()
    control = load_control()
    history = load_history()
    return jsonify(
        {
            "status": status,
            "control": control,
            "history": history,
        }
    ), 200 if status else 404


@dash_bp.route("/api/control", methods=["GET", "POST"])
def api_control():
    if request.method == "GET":
        return jsonify(load_control())

    payload = request.get_json(force=True, silent=True) or {}
    enabled = payload.get("trading_enabled")
    mode = payload.get("mode")
    updated = save_control(trading_enabled=enabled, mode=mode)
    return jsonify(updated)


@dash_bp.route("/api/history")
def api_history():
    return jsonify(load_history())
