#!/usr/bin/env python3
"""Render a timestamped diagrams.net editor page from any draw.io XML."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
from string import Template


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


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--diagram", default="diagram.xml", help="Path to the draw.io XML file to embed")
    parser.add_argument("--output", help="Custom output HTML file; defaults to diagram_editor_<timestamp>.html")
    parser.add_argument("--title", default="Diagram Snapshot", help="Page title / heading")
    parser.add_argument("--note", help="Optional paragraph under the heading")
    parser.add_argument("--iframe-url", default=DEFAULT_IFRAME_URL, help="diagrams.net embed URL")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    note = args.note or f"Generated {now.isoformat(timespec='seconds')} from {Path(args.diagram).name}."
    target = Path(args.output) if args.output else Path(f"diagram_editor_{timestamp}.html")

    result = generate_html(
        Path(args.diagram),
        target,
        title=args.title,
        note=note,
        iframe_url=args.iframe_url,
    )
    print(f"Wrote {result}")


if __name__ == "__main__":
    main()
