# PolyLab (Polymarket Scanner) - Gemini Context

This document provides essential context, architectural details, and operational workflows for the PolyLab project.

## 1. Project Overview
**PolyLab** is a high-performance scanner and analytics tool for [Polymarket](https://polymarket.com/). It aggregates market data, calculates metrics (APR, spread, liquidity), and provides a fast, filterable interface for finding betting opportunities.

## 2. Architecture & Tech Stack

### Backend
*   **Language**: Python 3.x
*   **Framework**: FastAPI (API + Static File Serving)
*   **Server**: Uvicorn
*   **Database**: SQLite (local file, WAL mode enabled for concurrency)
    *   `data/markets.db`: Main market data.
    *   `data/metrics.db`: Request logs and performance metrics.
*   **Data Ingestion**: `scraper.py` fetches data from Gamma/Polymarket APIs and rebuilds the DB.

### Frontend
*   **Architecture**: Single-file Static HTML/JS.
*   **Tech**: Vue.js (CDN), Tailwind CSS (CDN).
*   **Location**:
    *   `frontend_deploy/index.html`: The source of truth for the deployed frontend.
    *   `static/index.html`: Must be kept byte-identical to `frontend_deploy/index.html` (enforced by tests).
*   **Serving**: Served directly by FastAPI at `/` when `SERVE_FRONTEND=1`.

### Deployment
*   **Container**: Docker (`Dockerfile`, `docker-compose.yml`) includes Caddy as a reverse proxy.
*   **Platform**: optimized for VPS (Docker) or Vercel (Frontend only or Serverless split).

## 3. Key Files & Directories

*   `main.py`: Entry point. Configures FastAPI, serves API endpoints (`/api/*`), and serves frontend assets.
*   `scraper.py`: ETL script. Fetches markets/events from Gamma API and populates `markets.db`.
*   `gamma_client.py`: API client for Polymarket's Gamma API.
*   `tests/`: `unittest`-based test suite.
    *   `test_api_markets_unittest.py`: API correctness tests.
    *   `test_perf_simulation_unittest.py`: Performance regression tests (opt-in).
*   `docs/UI_CONTRACT.md`: Critical specification ensuring frontend/backend parity, especially for filters.
*   `AGENTS.md`: Meta-documentation for AI agents.

## 4. Operational Workflows

### Installation
```bash
python -m pip install -r requirements.txt
```

### Running Locally
**Standard Dev Mode:**
```bash
# Sets SERVE_FRONTEND=1 and ENABLE_DIAGNOSTICS=1
./dev_local.sh
```

**Manual Start:**
```bash
python main.py
```
*Access at `http://127.0.0.1:8000`*

### Database Management
The database is a local SQLite file in `data/`.
*   **Scrape/Refresh Data**: `python scraper.py`
*   **Schema**: Managed within `scraper.py` (rebuilds tables) and `main.py` (ensures indices/migrations on startup).

### Testing
**Run Standard Tests:**
```bash
python -m unittest discover -s tests -p "*_unittest.py"
```

**Run Performance Tests:**
```bash
RUN_PERF_TESTS=1 python -m unittest discover -s tests -p "*_unittest.py"
```
*Note: We do not use `fastapi.testclient.TestClient` due to `httpx` version conflicts. Tests call endpoint functions directly.*

## 5. Development Guidelines

*   **Performance First**: The application relies on SQLite's WAL mode and optimized indices. Always verify `ensure_indices()` in `main.py` when adding fields.
*   **Frontend Parity**: If you modify `frontend_deploy/index.html`, you **MUST** copy the changes to `static/index.html`.
*   **Conventions**:
    *   Use `snake_case` for Python variables/functions.
    *   Keep logic side-effect free where possible.
    *   Do not commit secrets or the SQLite database files (`data/*.db`).
*   **API Contract**: Strictly adhere to `docs/UI_CONTRACT.md` when modifying API parameters or responses. The frontend relies on specific field names and filter behaviors.

## 6. Common Tasks for Agents

*   **Adding a Filter**:
    1.  Update `get_markets` in `main.py` to handle the new query param.
    2.  Update SQLite indices in `ensure_indices` if performance is impacted.
    3.  Update `docs/UI_CONTRACT.md`.
    4.  Update frontend HTML to include the UI control.
    5.  Add a test case in `test_api_markets_unittest.py`.

*   **Optimizing Queries**:
    *   Use `EXPLAIN QUERY PLAN` (or the built-in perf logging in `main.py`) to analyze slow queries.
    *   Add indices in `main.py`.

*   **Debugging**:
    *   Check `data/metrics.db` or use `/api/admin/stats` for request latency data.

