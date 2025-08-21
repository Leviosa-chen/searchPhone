#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5000}"
URL="http://127.0.0.1:${PORT}/api/scrape"

# simple readiness probe: check index
if curl -fsS "http://127.0.0.1:${PORT}/" >/dev/null; then
  echo "OK"
else
  echo "NOT OK"
  exit 1
fi


