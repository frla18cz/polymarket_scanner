# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PolyLab is a Polymarket market scanner and analytics platform. Live at `https://www.polylab.app`, API at `https://api.polylab.app`.

## Commands

### Setup & Run
```bash
python -m pip install -r requirements.txt
python scraper.py      # Fetch initial market data into data/markets.db
./dev_local.sh         # Start dev server at http://127.0.0.1:8000
```

### Testing
```bash
# Run all unit tests (recommended)
CI=true python -m unittest discover -s tests -p "*_unittest.py"

# Run a single test file
CI=true python -m unittest tests/test_api_markets_unittest.py

# With performance tests (opt-in)
RUN_PERF_TESTS=1 python -m unittest discover -s tests -p "*_unittest.py"

# Rebuild integration test data (overwrites data/markets.db)
python tests/rebuild_test_data.py --limit 50 --yes
```

**Note:** Do not use `fastapi.testclient.TestClient` — tests call endpoint functions in `main.py` directly.

- `CI=true` prevents interactive prompts / watch-mode reruns — always use it when running tests
- `tests/_db_snapshot.py` provides `DbSnapshot` — creates an isolated temp copy of the DB via SQLite `.backup()` so tests never mutate production data

### Docker (VPS/Production)
```bash
docker compose up --build
```

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `MARKETS_DB_PATH` | `data/markets.db` | Path to main SQLite database |
| `METRICS_DB_PATH` | `data/metrics.db` | Path to metrics/telemetry database |
| `SERVE_FRONTEND` | unset | Set to `"1"` to enable frontend static file serving; otherwise frontend routes return 404 |
| `ENABLE_DIAGNOSTICS` | unset | Feature flag for diagnostics endpoints |
| `LOG_DIR` | `logs` | Directory for rotating log files |
| `LOG_TO_FILE` | `True` | When truthy, writes logs to rotating files; when falsy, logs only to stderr |
| `LOG_LEVEL` | `INFO` | Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

`dev_local.sh` sets `SERVE_FRONTEND=1`, `ENABLE_DIAGNOSTICS=1`, `LOG_TO_FILE=1` by default.

## Architecture

**Data flow:** External APIs → Worker (APScheduler) → SQLite → FastAPI → Vue frontend

### Key Files
| File | Purpose |
|------|---------|
| `main.py` | FastAPI server — API endpoints + static file serving |
| `auto_refresh.py` | Background scheduler (hourly: scraper → smart_money_scraper) |
| `scraper.py` | Market data ETL from Polymarket Gamma API |
| `smart_money_scraper.py` | Top-holder tracking and PnL aggregation |
| `gamma_client.py` | Client for Polymarket Gamma API |
| `holders_client.py` | Client for Polymarket Data/PnL APIs + Goldsky Subgraph |
| `frontend_deploy/index.html` | Single-file Vue 3 + Tailwind CSS frontend |

### Database (SQLite WAL mode)
- `data/markets.db` — market outcomes, tags, holders, wallet stats, smart money stats
- `data/metrics.db` — telemetry/request logs
- Backend reads **exclusively** from local SQLite — no external DB queries

### Frontend
Multi-page structure — each page has its own `index.html` under `frontend_deploy/`:

| Route | File | Purpose |
|-------|------|---------|
| `/` | `frontend_deploy/index.html` | Home / marketing page |
| `/app` | `frontend_deploy/app/index.html` | Scanner SPA (main product) |
| `/landing` | `frontend_deploy/landing/index.html` | Paid traffic landing page |
| `/custom-data` | `frontend_deploy/custom-data/index.html` | B2B / custom data funnel |

- Served by FastAPI when `SERVE_FRONTEND=1`; `/app/*` catchall supports SPA client-side routing
- `static/index.html` must stay **byte-identical** to `frontend_deploy/index.html` — enforced by a unit test
- **Always edit `frontend_deploy/index.html`, then copy to `static/index.html`**
- Assets served from `frontend_deploy/assets/` mounted at `/assets`

### Worker
`auto_refresh.py` runs APScheduler hourly. Execution is **sequential**: scraper completes before smart_money_scraper starts (no race conditions on the DB).

### API contract
See `docs/UI_CONTRACT.md`. Key endpoints:
- `GET /api/markets` — filterable market list (tags, price, spread, APR, liquidity, expiry, smart money)
- `GET /api/markets/{id}/holders` — top holders with PnL for a market
- `GET /api/tags` — tag list for filter autocomplete
- `GET /api/status` — `{ last_updated }` timestamp

Tag filter semantics: included tags use **ANY-match**; excluded tags remove a market if it has **any** excluded tag.

## Workflow

All development follows TDD (see `conductor/workflow.md`):
1. Pick task from active `plan.md` in `conductor/tracks/`
2. Mark task `[~]` in plan, write **failing** tests first
3. Implement minimum code to pass tests
4. Run coverage (target >80%)
5. Commit with `conductor(plan):` commit for plan updates

### Commit format
```
<type>(<scope>): <description>
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `conductor`

### Branching
- `development` — primary branch for ongoing work
- `main` — production branch (merged from `development` at milestones)

## Deployment Modes

| Mode | How | Notes |
|------|-----|-------|
| **Local dev** | `./dev_local.sh` | Single-process Uvicorn at `127.0.0.1:8000`, frontend + API together |
| **Docker Compose (VPS)** | `docker compose up --build` | 3 services: `web` (FastAPI), `worker` (APScheduler), `caddy` (reverse proxy + TLS) |
| **Vercel + VPS split** | `vercel.json` deploys `frontend_deploy/` | Static frontend on Vercel; API calls proxied to `https://api.polylab.app` on VPS |

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Uvicorn, APScheduler, Pydantic
- **Frontend:** Vue 3 (CDN), Tailwind CSS (CDN), Supabase Auth (frontend-only identity)
- **DB:** SQLite (WAL), two databases: `markets.db` + `metrics.db`
- **Testing:** pytest / unittest, Playwright (E2E/demo asset generation)
- **Infra:** Docker Compose, Caddy (reverse proxy)

Tech stack changes must be documented in `conductor/tech-stack.md` **before** implementation.

## Conductor (Source of Truth)

The `conductor/` directory drives all project planning and standards:
- **Active tracks** — `conductor/tracks/` contains current work streams, each with `plan.md`, `spec.md`, `index.md`
- **Code style guides** — `conductor/code_styleguides/` (general, python, javascript, html-css)
- **Workflow** — `conductor/workflow.md` (full TDD process)
- **Product** — `conductor/product.md` and `conductor/product-guidelines.md`
- **Tech stack** — `conductor/tech-stack.md` (approved tools and libraries)
