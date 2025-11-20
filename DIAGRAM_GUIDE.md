# Diagram Generation Guide

Keep the diagram XML inside draw.io-compatible bounds so `index.html` can embed it without fixes.

## Structure
- Wrap every export as `<mxfile><diagram><mxGraphModel>…` and keep the metadata attrs (`host`, `modified`, `agent`, `etag`, `version`, `type`).
- Start `<root>` with ids `0` and `1`; all other cells must reference an existing `parent`.
- Stick to `pageWidth="1200"` / `pageHeight="900"` so the iframe viewport lines up.

## Cells
- Unique `id` per `mxCell`; use readable labels like `widget`, `api`, `genai`.
- Vertices (`vertex="1"`) need an `mxGeometry` block with `x`, `y`, `width`, `height`.
- Edges (`edge="1"`) define `source`, `target`, and usually `mxGeometry relative="1"`.
- Groups/containers are vertices; their children set `parent` to that container and use local coordinates.

## Styling & Layout
- Use draw.io style keys (`shape`, `rounded`, `whiteSpace`, `html`, `fillColor`, `strokeColor`, …).
- Color palette: UI/API `#dae8fc/#6c8ebf`, Search `#d5e8d4/#82b366`, GenAI `#e1d5e7/#9673a6`, Safety `#f8cecc/#b85450`, notes `shape=note` + grey fill.
- Flow left→right (widget → API → Search → GenAI → Safety) with ~50–150 px margins.

## Validation
- Deliver plain XML (no comments or external includes).
- Run `python3 validate_xml.py` before importing or embedding.

Following these rules keeps `diagram.xml` drop-in ready for `index.html` and for `File > Import From…` inside diagrams.net.
