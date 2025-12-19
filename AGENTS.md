# Repository Guidelines

## Project Structure & Module Organization

- `main.py`: FastAPI app (API routes, DB access, diagnostics) and optional UI serving.
- `auto_refresh.py` / `scraper.py` / `gamma_client.py`: background refresh + Polymarket/Gamma fetching logic.
- `tests/`: unit tests and perf simulations (see `docs/TESTING.md`).
- `static/` and `frontend_deploy/`: built/served frontend assets (`index.html`, `assets/`).
- `data/`: local SQLite files (ignored by git) such as `data/markets.db` and `data/metrics.db`.

## Build, Test, and Development Commands

- Install deps: `python -m pip install -r requirements.txt`
- Run API locally: `python main.py` (defaults to `http://127.0.0.1:8000`)
- Local dev helper: `./dev_local.sh` (sets `SERVE_FRONTEND=1`, `ENABLE_DIAGNOSTICS=1`)
- Run with Docker: `docker compose up --build` (web + worker + Caddy reverse proxy)
- Frontend “build” (Vercel compatibility): `npm run build` (no-op by design; static HTML)

## Coding Style & Naming Conventions

- Python: 4-space indentation, keep functions small and side-effect boundaries clear (DB/network at edges).
- Prefer explicit names (`market_id`, `end_date`, `liquidity_usd`) and avoid “magic” globals; use env vars when configurable.
- Frontend: keep changes in sync between `static/index.html` and `frontend_deploy/index.html` when applicable.

## Testing Guidelines

- Tests are `unittest`-based and discovered via filename pattern `*_unittest.py`.
- Run tests: `python -m unittest discover -s tests -p "*_unittest.py"`
- Perf tests are opt-in: `RUN_PERF_TESTS=1 python -m unittest discover -s tests -p "*_unittest.py"`
- Note: tests call endpoint functions directly (not `TestClient`) due to httpx/TestClient version constraints (`docs/TESTING.md`).

## Commit & Pull Request Guidelines

- Commit messages commonly use lightweight prefixes: `fix: ...`, `feat: ...`, `perf: ...`, `ui: ...`, `docs: ...`, `chore: ...`.
- PRs: include a short “what/why”, link relevant issues/docs (e.g., `docs/UI_CONTRACT.md`), and add screenshots for UI changes.

## Security & Configuration Tips

- Never commit secrets; `.env` is local-only (ignored). Prefer env vars like `MARKETS_DB_PATH`, `METRICS_DB_PATH`.
- Don’t commit SQLite DBs or logs (`data/*.db`, `*.log` are ignored); use local snapshots for testing.
