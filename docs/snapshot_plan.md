# Snapshot Automation Plan

## Goals
- Every time `generate_html.py` runs, emit a standalone HTML snapshot whose filename includes a timestamp.
- Maintain/refresh an `snapshots/index.html` (or similar) that lists all generated snapshot files with human-friendly metadata so they can be opened later.
- Keep the solution minimally opinionated: pure Python tooling with no backend.

## Proposed Flow
1. **Directory Layout**
   - Store generated HTML files under `snapshots/diagram_editor_<timestamp>.html`.
   - Keep a template `snapshots/index_template.html` or embed minimal HTML directly from the script.
2. **Generator Enhancements**
   - Extend `generate_html.py` with a `--catalog` option (default `snapshots/index.html`).
   - After writing the snapshot file, update the catalog by:
     - Scanning the `snapshots/` directory for `*.html` (excluding the catalog itself).
     - Building a simple HTML list (most recent first) linking to each snapshot.
     - Optionally include metadata (title, note, timestamp) in the catalog entry using the data already passed to the generator.
3. **Metadata Persistence**
   - Each snapshot already stores `title` and `note`; write a sidecar JSON or embed metadata into the catalog by constructing entries on the fly from filenames and known parameters (timestamp from filename, note from CLI flag, etc.).
   - For richer metadata, create `snapshots/manifest.json` that the generator appends to; catalog HTML can read/parsing this JSON.
4. **Index HTML Structure**
   - Minimal static page listing snapshots, sorted desc.
   - Provide a short description and instructions.

## Implementation Steps
1. Update `generate_html.py`:
   - Add CLI args `--snapshot-dir` (default `snapshots`) and `--catalog snapshots/index.html`.
   - Ensure the snapshot dir exists.
   - Generate snapshot filename in that dir.
   - Append/update metadata (JSON manifest).
   - Regenerate catalog HTML from manifest (or direct directory scan).
2. Create `docs/` plan (this file) and later README snippet explaining the workflow.
3. Commit changes and document them in `CHANGELOG.md`.
