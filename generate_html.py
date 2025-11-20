#!/usr/bin/env python3
"""Render a timestamped diagrams.net editor page from any draw.io XML."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from string import Template
from typing import List, Dict


DEFAULT_IFRAME_URL = "https://embed.diagrams.net/?embed=1&ui=atlas&spin=1&proto=json"


HTML_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${title}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; background: #f8f9fa; }
        .header { padding: 1rem 1.5rem; border-bottom: 1px solid #dee2e6; background: #fff; }
        h1 { margin: 0; font-size: 1.4rem; }
        p { margin: 0.25rem 0 0; color: #6c757d; }
        iframe { flex: 1; border: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>${title}</h1>
        <p>${note}</p>
    </div>
    <iframe id="diagram-editor" frameborder="0"></iframe>
    <script>
        const diagramXML = `${diagram_xml}`;
        const iframe = document.getElementById('diagram-editor');

        function postMessage(message) {
            if (iframe.contentWindow) {
                iframe.contentWindow.postMessage(JSON.stringify(message), '*');
            }
        }

        window.addEventListener('message', (event) => {
            if (event.source !== iframe.contentWindow || !event.data) return;
            let msg = event.data;
            if (typeof msg === 'string') {
                try { msg = JSON.parse(msg); } catch (_) { return; }
            }
            if (typeof msg !== 'object') return;
            if (msg.event === 'configure') {
                postMessage({ action: 'configure', config: { defaultFonts: [], mathEnabled: false } });
            } else if (msg.event === 'init') {
                postMessage({ action: 'load', xml: diagramXML });
            }
        });

        iframe.src = '${iframe_url}';
    </script>
</body>
</html>
"""
)


def generate_html(diagram_path: Path, output_path: Path, *, title: str, note: str, iframe_url: str) -> Path:
    diagram_xml = diagram_path.read_text(encoding="utf-8")
    html = HTML_TEMPLATE.substitute(
        diagram_xml=diagram_xml,
        title=title,
        note=note,
        iframe_url=iframe_url,
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path


def load_manifest(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_manifest(path: Path, entries: List[Dict[str, str]]) -> None:
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def build_catalog(entries: List[Dict[str, str]], catalog_path: Path) -> None:
    rows = []
    for entry in entries:
        note = escape(entry.get("note", ""))
        title = escape(entry.get("title", entry.get("filename", "Diagram")))
        rows.append(
            f'<li><a href="{entry["filename"]}">{title}</a>'
            f'<br><small>{escape(entry.get("generated_at", ""))} · Source: '
            f'{escape(entry.get("diagram", ""))}<br>{note}</small></li>'
        )

    body = "\n        ".join(rows) if rows else "<p>No snapshots yet.</p>"

    catalog_html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Diagram Snapshots</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 2rem; background: #f8f9fa; }}
    h1 {{ margin-top: 0; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ background: #fff; border: 1px solid #dee2e6; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; }}
    a {{ font-weight: 600; color: #0d6efd; text-decoration: none; }}
    small {{ color: #6c757d; }}
  </style>
</head>
<body>
  <h1>Diagram Snapshots</h1>
  <p>Snapshots generated with <code>generate_html.py</code>. Newest first.</p>
  {'<ul>' if rows else ''}
  {body}
  {'</ul>' if rows else ''}
</body>
</html>
"""

    catalog_path.write_text(catalog_html, encoding="utf-8")


def relative_to(path: Path, base: Path) -> str:
    try:
        rel = path.resolve().relative_to(base.resolve())
    except ValueError:
        raise ValueError("Output file must live inside the snapshot directory to update the catalog.")
    return str(rel)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--diagram", default="diagram.xml", help="Path to the draw.io XML file to embed")
    parser.add_argument("--output", help="Custom output HTML file; defaults to <snapshot-dir>/diagram_editor_<timestamp>.html")
    parser.add_argument("--title", default="Diagram Snapshot", help="Page title / heading")
    parser.add_argument("--note", help="Optional paragraph under the heading")
    parser.add_argument("--iframe-url", default=DEFAULT_IFRAME_URL, help="diagrams.net embed URL")
    parser.add_argument("--snapshot-dir", default="snapshots", help="Directory for generated snapshots")
    parser.add_argument("--catalog", help="Catalog HTML output (default: <snapshot-dir>/index.html)")
    parser.add_argument("--manifest", help="Metadata JSON (default: <snapshot-dir>/manifest.json)")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    note = args.note or f"Generated {now.isoformat(timespec='seconds')} from {Path(args.diagram).name}."

    snapshot_dir = Path(args.snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        target = Path(args.output)
    else:
        target = snapshot_dir / f"diagram_editor_{timestamp}.html"

    title = escape(args.title)
    note_html = escape(note)
    result = generate_html(
        Path(args.diagram),
        target,
        title=title,
        note=note_html,
        iframe_url=args.iframe_url,
    )
    print(f"Wrote {result}")

    try:
        rel_name = relative_to(result, snapshot_dir)
    except ValueError:
        print(
            "Skipping catalog update: output file is outside the snapshot directory."
        )
        return

    manifest_path = Path(args.manifest) if args.manifest else snapshot_dir / "manifest.json"
    catalog_path = Path(args.catalog) if args.catalog else snapshot_dir / "index.html"

    entries = load_manifest(manifest_path)
    entries = [entry for entry in entries if entry.get("filename") != rel_name]
    entries.append(
        {
            "filename": rel_name,
            "title": args.title,
            "note": note,
            "generated_at": now.isoformat(timespec="seconds"),
            "diagram": str(Path(args.diagram)),
            "iframe_url": args.iframe_url,
        }
    )
    entries.sort(key=lambda e: e.get("generated_at", ""), reverse=True)
    save_manifest(manifest_path, entries)
    build_catalog(entries, catalog_path)
    print(f"Updated catalog at {catalog_path}")


if __name__ == "__main__":
    main()
