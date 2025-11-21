# Auto-save & Versioned Snapshots Plan

## Goals
1. Enable the embedded diagrams.net editor to persist its XML directly from the browser without manual export.
2. Maintain version history (timestamped files + Git-friendly workflow) for each save.
3. Keep the workflow simple enough to run locally (no external services beyond Python runtime), but expandable later.

## Proposed Architecture
- **Backend:** Lightweight Flask (or FastAPI) server running alongside the static files.
  - Serves the existing static assets (index.html, editor.html, snapshots, etc.) via `send_from_directory` or a tiny static server (or continue using `http.server` for static files and only use Flask for APIs).
  - Exposes REST endpoints for saving and listing versions.
- **Data storage:**
  - Write every POSTed XML to `snapshots/raw/<timestamp>.xml` (preserves full history).
  - Optionally run `generate_html.py` after each save to produce the HTML preview + update catalog automatically.
  - Maintain a JSON manifest (`snapshots/manifest.json`, already in use). Backend appends new entries here.
- **Version control integration:**
  - Optionally auto-run `git add snapshots/raw/<file> snapshots/index.html manifest.json` + `git commit -m "Auto save <timestamp>"` if repo is clean (configurable flag for advanced users).
- **Security:**
  - Local dev server only; no authentication by default. Document that it’s for local usage (trusted environment).

## API Endpoints
1. `POST /api/save`
   - Request body: JSON with `{ "xml": "...", "title": "optional", "note": "optional" }`.
   - Actions:
     1. Validate XML (via `xml.etree.ElementTree.fromstring`).
     2. Persist raw XML file under `snapshots/raw/diagram_<timestamp>.xml`.
     3. Run `generate_html.py --diagram <new_file> --title ... --note ...` to create a snapshot HTML and refresh catalog.
     4. Respond with metadata `{ "timestamp": ..., "snapshot": "snapshots/diagram_editor_...html" }`.
2. `GET /api/versions`
   - Returns the current manifest (JSON) so the UI can show previous saves without loading the iframe catalog.
3. (Optional) `GET /api/latest`
   - Returns the latest raw XML so the editor can load it automatically (avoiding manual copy into `editor.html`).

## Frontend Integration
- In `editor.html`, listen to diagrams.net `export` / `autosave` messages:
  - Use the postMessage API to request the XML (`{ action: 'export', format: 'xml', xml: 1 }`).
  - On response, send an AJAX `POST /api/save` with the XML payload.
  - Display success/failure notifications.
- Add a “Save to snapshots” button in the header that triggers the export + POST flow.
- Optionally auto-save on intervals or when the user clicks existing Save in diagrams.net (if the embed exposes `autosave` events).
- diagrams.net also emits `save`/`autosave` events (see [draw.io embed docs](https://www.diagrams.net/doc/faq/embed-mode)); we can intercept `msg.event === 'save'` to:
  1. Call `postMessage({ action: 'export', format: 'xml' })` to fetch the XML.
  2. Send it to the backend automatically, so the built-in Save button works seamlessly.
- Add a breadcrumb/header bar outside the iframe showing:
  - Link back to `index.html` + snapshot listing.
  - Dropdown listing the last few versions (fetched from `/api/versions`). Selecting one opens the snapshot or loads its XML via API.
  - “Save snapshot” button for manual saves.

## File Layout Changes
```
project/
  app.py                 # Flask server with API endpoints
  static/                # (optional) hold index.html/editor.html or keep root
  snapshots/
    raw/                 # New folder for raw XML versions
    manifest.json        # Already exists (extend schema for raw file)
    index.html           # Catalog rebuilt by generate_html.py
    diagram_editor_*.html
```

## Implementation Steps
1. **Backend setup**
   - Add Flask dependency + `requirements.txt`.
   - Create `app.py` with the endpoints above.
   - Ensure CORS is not required (same origin) by serving frontend and API from same host/port.
2. **Saving pipeline**
   - Implement POST handler: validate XML, write raw file, run generator (maybe by importing `generate_html` functions).
   - Update manifest schema to include `raw_xml_path`.
3. **Frontend wiring**
   - Update `editor.html` script to add “Save snapshot” button → request export → POST to API.
   - Show status to user.
4. **Version listing**
   - Optionally update `index.html` to fetch `/api/versions` and render a dynamic list (instead of iframe), while keeping the static catalog for direct browsing.
5. **Docs & scripts**
   - Document how to run the Flask server (`python3 app.py`) and how it interacts with git/history.
   - Update README + CHANGELOG.
6. **Future enhancements**
   - Add optional `git commit` integration.
   - Support editing non-default diagram by passing IDs/tags in API.

With this plan we can iterate incrementally: first build the POST endpoint + manual button, then consider auto-save or git integration.
