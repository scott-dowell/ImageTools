import os
import shutil
import threading
from datetime import datetime
from pathlib import Path, PurePath

from flask import Flask, jsonify, make_response, render_template, request

from converter import build_folder_progress_summary, convert_tree, discover_image_files, summarize_folder_status, update_folder_statuses

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

_run_lock = threading.Lock()
_run_state = {
    "state": "idle",
    "phase": "idle",
    "root": "",
    "total": 0,
    "folders": [],
    "processed": 0,
    "converted_count": 0,
    "skipped_count": 0,
    "current_file": "",
    "progress_percent": 0.0,
    "saved_bytes": 0,
    "eta_seconds": 0,
    "started_at": None,
    "completed_at": None,
    "result": None,
    "processed_paths": [],
    "completed_paths": [],
}


def _run_state_for_json() -> dict:
    with _run_lock:
        state = dict(_run_state)
        for key in ("started_at", "completed_at"):
            value = state.get(key)
            if isinstance(value, datetime):
                state[key] = value.isoformat()
        if state.get("state") == "running" and state.get("started_at") and state.get("total"):
            started_at = state.get("started_at")
            if isinstance(started_at, datetime):
                elapsed_seconds = max(1, int((datetime.utcnow() - started_at).total_seconds()))
            else:
                elapsed_seconds = 1
            processed = int(state.get("processed", 0) or 0)
            total = int(state.get("total", 0) or 0)
            if processed > 0 and total > processed:
                eta_seconds = int((elapsed_seconds / processed) * (total - processed))
            else:
                eta_seconds = 0
            state["eta_seconds"] = max(0, eta_seconds)
        else:
            state["eta_seconds"] = 0
        state.pop("processed_paths", None)
        state.pop("completed_paths", None)
        return state


def _update_run_state(**updates) -> None:
    with _run_lock:
        _run_state.update(updates)
        if _run_state.get("state") in {"idle", "done"}:
            _run_state["current_file"] = ""
            _run_state["progress_percent"] = 0.0


def select_folder_path(chooser=None) -> str:
    chooser = chooser or (lambda: str(Path.cwd()))
    return str(chooser()).strip()


def write_uploaded_folder(uploads: list, destination_root: str | Path, folder_name: str) -> Path:
    destination_root_path = Path(destination_root)
    target_root = destination_root_path / folder_name
    target_root.mkdir(parents=True, exist_ok=True)

    for upload in uploads or []:
        name = getattr(upload, "filename", "") or ""
        if not name:
            continue
        relative_name = str(Path(name).as_posix())
        destination_path = target_root / relative_name
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(upload, "save"):
            upload.save(destination_path)
        else:
            destination_path.write_bytes(b"")

    return target_root


def _normalize_folder_path(path: str) -> str:
    return str(Path(path).resolve()).replace("\\", "/")


def _path_has_directory_children(path: Path) -> bool:
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                try:
                    if entry.is_dir():
                        return True
                except (PermissionError, OSError):
                    continue
    except (PermissionError, FileNotFoundError, NotADirectoryError, OSError):
        return False
    return False


def _resolve_folder_path(path: str) -> str:
    path_obj = Path(path)
    resolved_path = path_obj.resolve()
    if resolved_path.name and resolved_path.suffix:
        return _normalize_folder_path(resolved_path.parent)
    return _normalize_folder_path(resolved_path)


def _update_folder_statuses_for_progress(statuses: list[dict], current_path: str, previous_path: str | None = None) -> tuple[list[dict], str]:
    current_folder = _resolve_folder_path(current_path)
    normalized_current_folder = _normalize_folder_path(current_folder)
    updated = [dict(item) for item in statuses]

    if previous_path:
        previous_folder = _resolve_folder_path(previous_path)
        normalized_previous_folder = _normalize_folder_path(previous_folder)
        if normalized_previous_folder != normalized_current_folder:
            for item in updated:
                if _normalize_folder_path(item.get("folder", "")) == normalized_previous_folder:
                    item["status"] = "done"
                    break

    for item in updated:
        if _normalize_folder_path(item.get("folder", "")) == normalized_current_folder:
            item["status"] = "converting"
            break

    return updated, current_folder


def _on_progress(processed: int, total: int, current_path: str, conversion_result: dict | None = None) -> None:
    with _run_lock:
        previous_path = _run_state.get("current_file") or None

        _run_state["processed"] = processed
        _run_state["total"] = total
        _run_state["current_file"] = current_path
        _run_state["progress_percent"] = round((processed / total * 100.0) if total else 100.0, 1)
        _run_state["state"] = "running"
        _run_state["phase"] = "converting"
        _run_state["processed_paths"] = []
        _run_state["completed_paths"] = []
        if _run_state.get("folders"):
            _run_state["folders"], _ = _update_folder_statuses_for_progress(
                _run_state["folders"],
                current_path,
                previous_path,
            )
            folder_summaries = [dict(item) for item in _run_state.get("folders", [])]
            if conversion_result is not None:
                folder_path = str(Path(current_path).parent)
                for folder_item in folder_summaries:
                    if _normalize_folder_path(folder_item.get("folder", "")) == _normalize_folder_path(folder_path):
                        if conversion_result is not None:
                            if conversion_result.get("status") == "converted":
                                folder_item["converted"] += 1
                                if not folder_item.get("size_before_bytes", 0):
                                    folder_item["size_before_bytes"] = int(conversion_result.get("size_before_bytes", 0) or 0)
                                size_before_bytes = int(conversion_result.get("size_before_bytes", 0) or 0)
                                folder_item["size_before_bytes_for_percent"] = int(folder_item.get("size_before_bytes_for_percent", 0) or 0) + size_before_bytes
                                folder_item["size_after_bytes"] += int(conversion_result.get("size_after_bytes", 0) or 0)
                                folder_item["saved_bytes"] += int(conversion_result.get("saved_bytes", 0) or 0)
                                _run_state["saved_bytes"] = int(_run_state.get("saved_bytes", 0) or 0) + int(conversion_result.get("saved_bytes", 0) or 0)
                            elif conversion_result.get("status") in {"failed", "skipped"}:
                                folder_item["skipped"] += 1
                        else:
                            folder_item["converted"] += 1
                        folder_item["progress"] = int(round((folder_item.get("converted", 0) + folder_item.get("skipped", 0)) / folder_item["count"] * 100)) if folder_item["count"] else 100
                        percent_baseline = folder_item.get("size_before_bytes_for_percent", 0) or folder_item.get("size_before_bytes", 0)
                        if percent_baseline > 0:
                            folder_item["savings_percent"] = int(round((folder_item.get("saved_bytes", 0) / max(percent_baseline, 1)) * 100)) if percent_baseline else 0
                            folder_item["savings_percent"] = max(0, min(100, folder_item["savings_percent"]))
                        break
            _run_state["folders"] = folder_summaries


def _run_conversion(root: str, quality: int) -> None:
    folder_summary = summarize_folder_status(root)
    discovered_files = discover_image_files(root)
    _update_run_state(
        state="running",
        phase="converting",
        root=root,
        total=len(discovered_files),
        processed=0,
        converted_count=0,
        skipped_count=0,
        current_file="",
        progress_percent=0.0,
        saved_bytes=0,
        started_at=datetime.utcnow(),
        completed_at=None,
        result=None,
        folders=folder_summary,
        processed_paths=[],
        completed_paths=[],
    )
    result = convert_tree(root, quality=quality, on_progress=_on_progress)
    with _run_lock:
        folder_progress = result.get("folder_progress", _run_state.get("folders", []))
        for folder in folder_progress:
            if folder.get("status") in {"converting", "pending"} and folder.get("progress", 0) >= 100:
                folder["status"] = "done"
            elif folder.get("status") == "converting":
                folder["status"] = "done"

        _run_state["folders"] = folder_progress

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
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/api/scan", methods=["POST"])
def scan_folder():
    payload = request.get_json(silent=True) or {}
    root = payload.get("root") or ""
    if not root:
        return jsonify({"error": "No root folder specified"}), 400

    root_path = Path(root)
    files = discover_image_files(root_path)
    folder_summary = summarize_folder_status(root_path)
    return jsonify({
        "root": str(root_path),
        "count": len(files),
        "files": [str(path) for path in files[:200]],
        "folders": folder_summary,
    })


@app.route("/api/browse", methods=["GET"])
def browse_folder():
    path = request.args.get("path") or ""
    try:
        base_path = Path(path).expanduser() if path else Path.cwd()
        resolved_path = base_path.resolve()
        if not resolved_path.exists():
            resolved_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        resolved_path = Path.cwd()

    directories = []
    try:
        children = sorted(resolved_path.iterdir(), key=lambda item: item.name.lower())
    except (PermissionError, FileNotFoundError, NotADirectoryError, OSError):
        children = []

    for child in children:
        if not child.name.startswith(".") and child.is_dir():
            directories.append({
                "name": child.name,
                "full_path": str(child),
                "has_children": _path_has_directory_children(child),
            })

    return jsonify({
        "path": str(resolved_path),
        "parent": str(resolved_path.parent) if resolved_path.parent != resolved_path else None,
        "dirs": directories,
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
