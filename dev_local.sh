#!/usr/bin/env bash
set -euo pipefail

export ENABLE_DIAGNOSTICS="${ENABLE_DIAGNOSTICS:-1}"
export SERVE_FRONTEND="${SERVE_FRONTEND:-1}"

echo "Backend: http://127.0.0.1:8000 (SERVE_FRONTEND=$SERVE_FRONTEND, ENABLE_DIAGNOSTICS=$ENABLE_DIAGNOSTICS)"
echo "Diagnostics: http://127.0.0.1:8000/api/diagnostics/perf?mode=fast"

python main.py

