# Changelog

## 2024-11-19
- Switched the embedded diagrams.net editor (`index.html`) to the JSON postMessage protocol with a configure handshake so the iframe stops hanging on "Loading".
- Updated the diagram assets (`diagram.xml` and inline XML in `index.html`) with Finnish labels, wider nodes, and balanced spacing for a visually consistent layout.
- Added `DIAGRAM_GUIDE.md` to capture the draw.io formatting constraints for any future AI-generated diagrams.
- Rewrote `DIAGRAM_GUIDE.md` in concise English so models can follow it without translation overhead.
- Added `generate_html.py` to emit timestamped HTML snapshots that embed the diagrams.net editor plus the current XML, and later generalized it to accept custom diagram paths, titles, notes, and iframe URLs.
