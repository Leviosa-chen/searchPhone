#!/usr/bin/env bash
set -euo pipefail

# 命令行参数解析
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --workers)
      WORKERS="$2"
      shift 2
      ;;
    --max-pages)
      MAX_PAGES="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--port PORT] [--workers WORKERS] [--max-pages MAX_PAGES]"
      echo "  --port PORT        Port to bind (default: 5000)"
      echo "  --workers WORKERS  Number of worker processes (default: 2)"
      echo "  --max-pages PAGES  Default max pages to crawl (default: 200)"
      echo "  --help            Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                    # 使用默认配置"
      echo "  $0 --port 8080       # 指定端口 8080"
      echo "  $0 --port 8080 --workers 4 --max-pages 100"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Config - 支持环境变量覆盖
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="python3"
VENV_DIR="$APP_DIR/.venv"
PORT="${PORT:-5000}"  # 支持环境变量 PORT 覆盖
HOST="0.0.0.0"
WORKERS="${WORKERS:-2}"  # 支持环境变量 WORKERS 覆盖
MAX_PAGES_DEFAULT="${MAX_PAGES:-200}"  # 支持环境变量 MAX_PAGES 覆盖

echo "[deploy] App dir: $APP_DIR"
echo "[deploy] Port: $PORT"
echo "[deploy] Workers: $WORKERS"
echo "[deploy] Max pages: $MAX_PAGES_DEFAULT"

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
    echo "[deploy] Service started successfully!"
    echo "[deploy] PID: $GUNICORN_PID"
    echo "[deploy] Log: $APP_DIR/gunicorn.out"
    echo "[deploy] Access: http://$(hostname -I | awk '{print $1}'):$PORT"
    exit 0
  fi
  sleep 1
done

echo "[deploy] Service failed to become healthy. See $APP_DIR/gunicorn.out"
exit 1


