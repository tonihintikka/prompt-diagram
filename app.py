from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from flask import Flask, jsonify, request, send_from_directory

from generate_html import (
    DEFAULT_IFRAME_URL,
    build_catalog,
    generate_html as build_snapshot,
    load_manifest,
    relative_to,
    save_manifest,
)

ROOT = Path(__file__).resolve().parent
SNAPSHOT_DIR = ROOT / "snapshots"
RAW_DIR = SNAPSHOT_DIR / "raw"
MANIFEST_PATH = SNAPSHOT_DIR / "manifest.json"
CATALOG_PATH = SNAPSHOT_DIR / "index.html"
CURRENT_DIAGRAM = ROOT / "diagram_workflow.xml"
FALLBACK_DIAGRAM = ROOT / "diagram.xml"

SNAPSHOT_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


def get_active_diagram() -> Path:
    if CURRENT_DIAGRAM.exists():
        return CURRENT_DIAGRAM
    if FALLBACK_DIAGRAM.exists():
        return FALLBACK_DIAGRAM
    raise FileNotFoundError("No diagram file found")


def load_current_xml() -> str:
    path = get_active_diagram()
    return path.read_text(encoding="utf-8"), path


def create_snapshot(diagram_path: Path, *, title: str, note: str) -> dict:
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    output_path = SNAPSHOT_DIR / f"diagram_editor_{timestamp}.html"

    build_snapshot(
        diagram_path,
        output_path,
        title=escape(title),
        note=escape(note),
        iframe_url=DEFAULT_IFRAME_URL,
    )

    rel_name = relative_to(output_path, SNAPSHOT_DIR)
    entries = load_manifest(MANIFEST_PATH)
    entries = [entry for entry in entries if entry.get("filename") != rel_name]
    try:
        diagram_rel = diagram_path.relative_to(ROOT)
    except ValueError:
        diagram_rel = diagram_path

    entry = {
        "filename": rel_name,
        "title": title,
        "note": note,
        "generated_at": now.isoformat(timespec="seconds"),
        "diagram": str(diagram_rel),
    }
    entries.append(entry)
    entries.sort(key=lambda item: item.get("generated_at", ""), reverse=True)
    save_manifest(MANIFEST_PATH, entries)
    build_catalog(entries, CATALOG_PATH)
    return entry


@app.route("/api/latest")
def api_latest():
    try:
        xml_text, path = load_current_xml()
    except FileNotFoundError:
        return jsonify({"error": "No diagram available"}), 404

    return jsonify(
        {
            "xml": xml_text,
            "source": str(path.relative_to(ROOT)),
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(
                timespec="seconds"
            ),
        }
    )


@app.route("/api/versions")
def api_versions():
    entries = load_manifest(MANIFEST_PATH)
    return jsonify(entries)


@app.route("/api/save", methods=["POST"])
def api_save():
    payload = request.get_json(silent=True) or {}
    xml = payload.get("xml")
    if not xml:
        return jsonify({"error": "Missing xml"}), 400

    try:
        ET.fromstring(xml)
    except ET.ParseError as exc:
        return jsonify({"error": f"Invalid XML: {exc}"}), 400

    title = payload.get("title") or "Auto-save snapshot"
    note = payload.get("note") or "Saved from embedded editor"

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    raw_path = RAW_DIR / f"diagram_{timestamp}.xml"
    raw_path.write_text(xml, encoding="utf-8")

    # Update the active diagram so the editor reloads latest content
    current_path = get_active_diagram()
    current_path.write_text(xml, encoding="utf-8")

    entry = create_snapshot(raw_path, title=title, note=note)

    response = {
        "status": "ok",
        "timestamp": entry["generated_at"],
        "snapshot": entry["filename"],
        "raw_xml": str(raw_path.relative_to(ROOT)),
    }
    return jsonify(response), 201


@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path: str):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True)
