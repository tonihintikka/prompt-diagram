#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
HOST="127.0.0.1"
PORT="5000"
URL="http://${HOST}:${PORT}/index.html"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install -r requirements.txt >/dev/null

( sleep 1 && python3 - <<PY
import webbrowser
webbrowser.open("${URL}")
PY
) &

exec python3 app.py
