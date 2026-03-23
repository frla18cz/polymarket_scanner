#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-$HOME/polymarket_scanner}"
BRANCH="${BRANCH:-main}"
API_ORIGIN="${API_ORIGIN:-https://api.polylab.app}"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Missing docker compose / docker-compose" >&2
  exit 1
fi

cd "$APP_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "APP_DIR is not a git repository: $APP_DIR" >&2
  exit 1
fi

echo "[1/8] Fetch latest code"
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "[2/8] Optional DB backup"
mkdir -p backups
if [ -f data/markets.db ]; then
  cp data/markets.db "backups/markets_$(date +%Y%m%d_%H%M%S).db"
fi

echo "[3/8] Rebuild and restart services"
"${COMPOSE_CMD[@]}" up -d --build

echo "[4/8] Warm materialized smart-money stats"
"${COMPOSE_CMD[@]}" exec -T web python - <<'PY'
import main
main.refresh_materialized_smart_money_stats()
print("materialized smart money refreshed")
PY

echo "[5/8] Warm bootstrap snapshots"
"${COMPOSE_CMD[@]}" exec -T web python - <<'PY'
import main
main.refresh_bootstrap_snapshots()
print("bootstrap snapshots refreshed")
PY

echo "[6/8] Health checks"
curl -fsS "${API_ORIGIN}/api/status" >/tmp/polylab_status.json
curl -fsS "${API_ORIGIN}/api/homepage-bootstrap" >/tmp/polylab_homepage_bootstrap.json
curl -fsS "${API_ORIGIN}/api/app-bootstrap?view=scanner" >/tmp/polylab_app_scanner_bootstrap.json
curl -fsS "${API_ORIGIN}/api/app-bootstrap?view=smart&preset=smart_money_edge" >/tmp/polylab_app_smart_bootstrap.json

echo "[7/8] Service status"
"${COMPOSE_CMD[@]}" ps

echo "[8/8] Recent logs"
"${COMPOSE_CMD[@]}" logs --tail=80 web worker

echo "Deploy complete"
