# Changelog

## 2024-11-19
- Switched the embedded diagrams.net editor (`index.html`) to the JSON postMessage protocol with a configure handshake so the iframe stops hanging on "Loading".
- Updated the diagram assets (`diagram.xml` and inline XML in `index.html`) with Finnish labels, wider nodes, and balanced spacing for a visually consistent layout.
- Added `DIAGRAM_GUIDE.md` to capture the draw.io formatting constraints for any future AI-generated diagrams.
- Rewrote `DIAGRAM_GUIDE.md` in concise English so models can follow it without translation overhead.
- Added `generate_html.py` to emit timestamped HTML snapshots that embed the diagrams.net editor plus the current XML, and later generalized it to accept custom diagram paths, titles, notes, iframe URLs, snapshot directories, and to auto-maintain `snapshots/index.html` + `manifest.json`.
- Introduced a Flask-based autosave API (`app.py`) plus toolbar updates in `editor.html` so the built-in Save button exports XML to the server, stores raw versions under `snapshots/raw/`, and regenerates the HTML snapshot catalog automatically.
- Added `requirements.txt` and documentation updates describing how to run the autosave server.
- Added `run_server.sh` helper script that bootstraps a `.venv`, installs dependencies, runs `app.py`, and opens the browser automatically.
