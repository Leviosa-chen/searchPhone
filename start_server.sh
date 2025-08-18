#!/usr/bin/env bash
set -euo pipefail

# Config
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="python3"
VENV_DIR="$APP_DIR/.venv"
PORT="5000"
HOST="0.0.0.0"
WORKERS="2"
MAX_PAGES_DEFAULT="200"

echo "[deploy] App dir: $APP_DIR"

# 1) Ensure Python and venv
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[deploy] python3 not found. Please install python3." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[deploy] Create venv..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
pip install -r "$APP_DIR/requirements.txt"

# 2) Create outputs dir
mkdir -p "$APP_DIR/outputs"

# 3) Healthcheck endpoint (background)
HEALTH_URL="http://127.0.0.1:$PORT/"

# 4) Start gunicorn
export MAX_PAGES="$MAX_PAGES_DEFAULT"
export PORT="$PORT"
export FLASK_APP="web_app:app"

echo "[deploy] Starting gunicorn on $HOST:$PORT ..."
cd "$APP_DIR"
nohup gunicorn \
  --bind "$HOST:$PORT" \
  --workers "$WORKERS" \
  --timeout 300 \
  --log-level info \
  web_app:app > "$APP_DIR/gunicorn.out" 2>&1 &
GUNICORN_PID=$!
echo "$GUNICORN_PID" > "$APP_DIR/gunicorn.pid"

# 5) Wait for healthy
echo "[deploy] Waiting for health..."
ATTEMPTS=30
for i in $(seq 1 $ATTEMPTS); do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "[deploy] Service is healthy on $HEALTH_URL"
    exit 0
  fi
  sleep 1
done

echo "[deploy] Service failed to become healthy. See $APP_DIR/gunicorn.out"
exit 1


