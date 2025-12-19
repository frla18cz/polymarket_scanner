#!/usr/bin/env bash
set -euo pipefail

export ENABLE_DIAGNOSTICS="${ENABLE_DIAGNOSTICS:-1}"
export SERVE_FRONTEND="${SERVE_FRONTEND:-1}"
export LOG_DIR="${LOG_DIR:-logs}"
export LOG_TO_FILE="${LOG_TO_FILE:-1}"

LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
if [ -n "${LAN_IP:-}" ]; then
  echo "Backend (LAN): http://${LAN_IP}:8000"
fi
echo "Backend (local): http://127.0.0.1:8000 (SERVE_FRONTEND=$SERVE_FRONTEND, ENABLE_DIAGNOSTICS=$ENABLE_DIAGNOSTICS)"
echo "Diagnostics: http://127.0.0.1:8000/api/diagnostics/perf?mode=fast"

python main.py
