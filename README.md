# Generative Diagram Editor

This project hosts a single-page helper that embeds the diagrams.net (draw.io) editor with a preloaded architecture diagram. The goal is to enable AI-generated draw.io XML to be reviewed, tweaked, and exported entirely in the browser without setting up additional infrastructure.

## Repository Structure
- `index.html` – Minimal UI chrome plus the iframe integration that loads diagrams.net via `proto=json` messaging and injects the bundled XML.
- `diagram.xml` – Standalone draw.io file (Finnish labels) that mirrors the inline XML string in `index.html` for easy editing/importing.
- `DIAGRAM_GUIDE.md` – Constraints for future AI agents so they output draw.io-compatible structures.
- `validate_xml.py` – Simple well-formedness check for `diagram.xml` using Python's `xml.etree.ElementTree`.
- `generate_html.py` – Utility that snapshots the current diagram into a timestamped HTML page containing the same embedded editor.
- `CHANGELOG.md` – Release notes.

## Running the Editor Locally
1. Start any static file server in the project root, e.g. `python3 -m http.server 8888`.
2. Open `http://localhost:8888/index.html` in a browser.
3. diagrams.net loads inside the iframe, pre-populated with the XML defined in `diagram.xml`/`index.html`.

## Editing the Diagram
- To tweak the diagram in draw.io, edit it directly inside the iframe and then export (`File → Export as…`) or save (`File → Save As…`).
- To update the bundled XML, export to XML from the editor, replace the contents of `diagram.xml`, and copy the same XML into the `diagramXML` string inside `index.html` (or automate this step).
- Before importing into draw.io, you can run `python3 validate_xml.py` to ensure the XML is well-formed.

## Generating Timestamped Snapshots
- Run `python3 generate_html.py` to produce `snapshots/diagram_editor_<timestamp>.html` embedding the latest XML.
- The script also maintains `snapshots/manifest.json` and regenerates `snapshots/index.html`, which lists every snapshot (newest first) with its metadata.
- Useful CLI flags:
  - `--diagram other.xml` – embed a different draw.io file.
  - `--title "My Architecture"` / `--note "Generated for demo"` – customize the snapshot header.
  - `--iframe-url <url>` – swap to another diagrams.net deployment if needed.
  - `--snapshot-dir custom_dir` / `--catalog custom_dir/index.html` – change where snapshots and the catalog live.
  - `--output custom.html` – override the auto-generated filename (must reside inside the snapshot dir to appear in the catalog).

## Generating New Diagrams via AI
If you ask an AI model to produce a new diagram, point it to `DIAGRAM_GUIDE.md`. The guide explains:
- Required `mxfile > diagram > mxGraphModel` structure.
- Naming conventions for cells and parents.
- Style palette (colors, shapes, note formatting) to keep the visual identity consistent.
- Page dimensions and layout expectations.

Keeping AI-generated output within those constraints ensures the iframe can import the diagram without manual repair.
