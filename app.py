import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from converter import convert_tree, discover_image_files

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


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
    return jsonify({
        "root": str(root_path),
        "count": len(files),
        "files": [str(path) for path in files[:200]],
    })


@app.route("/api/convert", methods=["POST"])
def convert_folder():
    payload = request.get_json(silent=True) or {}
    root = payload.get("root") or ""
    quality = int(payload.get("quality", 85))
    if not root:
        return jsonify({"error": "No root folder specified"}), 400

    result = convert_tree(root, quality=quality)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
