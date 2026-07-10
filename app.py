import os
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from converter import convert_tree, discover_image_files, summarize_image_counts_by_folder

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

_run_lock = threading.Lock()
_run_state = {
    "state": "idle",
    "phase": "idle",
    "root": "",
    "total": 0,
    "processed": 0,
    "converted_count": 0,
    "skipped_count": 0,
    "current_file": "",
    "progress_percent": 0.0,
    "started_at": None,
    "completed_at": None,
    "result": None,
}


def _run_state_for_json() -> dict:
    with _run_lock:
        state = dict(_run_state)
        for key in ("started_at", "completed_at"):
            value = state.get(key)
            if isinstance(value, datetime):
                state[key] = value.isoformat()
        return state


def _update_run_state(**updates) -> None:
    with _run_lock:
        _run_state.update(updates)


def _on_progress(processed: int, total: int, current_path: str) -> None:
    with _run_lock:
        _run_state["processed"] = processed
        _run_state["total"] = total
        _run_state["current_file"] = current_path
        _run_state["progress_percent"] = round((processed / total * 100.0) if total else 100.0, 1)
        _run_state["state"] = "running"
        _run_state["phase"] = "converting"


def _run_conversion(root: str, quality: int) -> None:
    _update_run_state(
        state="running",
        phase="converting",
        root=root,
        total=0,
        processed=0,
        converted_count=0,
        skipped_count=0,
        current_file="",
        progress_percent=0.0,
        started_at=datetime.utcnow(),
        completed_at=None,
        result=None,
    )
    result = convert_tree(root, quality=quality, on_progress=_on_progress)
    _update_run_state(
        state="done",
        phase="complete",
        converted_count=result.get("converted_count", 0),
        skipped_count=result.get("skipped_count", 0),
        completed_at=datetime.utcnow(),
        result=result,
    )


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan_folder():
    payload = request.get_json(silent=True) or {}
    root = payload.get("root") or ""
    if not root:
        return jsonify({"error": "No root folder specified"}), 400

    root_path = Path(root)
    files = discover_image_files(root_path)
    folder_summary = summarize_image_counts_by_folder(root_path)
    return jsonify({
        "root": str(root_path),
        "count": len(files),
        "files": [str(path) for path in files[:200]],
        "folders": folder_summary,
    })


@app.route("/api/convert", methods=["POST"])
def convert_folder():
    payload = request.get_json(silent=True) or {}
    root = payload.get("root") or ""
    quality = int(payload.get("quality", 85))
    if not root:
        return jsonify({"error": "No root folder specified"}), 400

    with _run_lock:
        if _run_state["state"] == "running":
            return jsonify({"error": "A conversion is already running"}), 409

    threading.Thread(target=_run_conversion, args=(root, quality), daemon=True).start()
    return jsonify({"status": "started", "run": _run_state_for_json()})


@app.route("/api/progress")
def progress_status():
    return jsonify(_run_state_for_json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
