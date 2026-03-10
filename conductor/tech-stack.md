# Technology Stack: PolyLab

## 1. Backend
*   **Language:** Python 3.12+
*   **Framework:** **FastAPI** for high-performance API endpoints and static file serving.
*   **Server:** **Uvicorn** as the ASGI web server.
*   **Scheduler:** **APScheduler** for robust background task management.
*   **Data Validation:** **Pydantic** for schema enforcement and type safety.

## 2. Frontend
*   **Architecture:** Single-file Static HTML/JS.
*   **Framework:** **Vue.js** (CDN-hosted) for reactive UI components.
*   **Styling:** **Tailwind CSS** (CDN-hosted) for rapid UI development and styling.
*   **Strategy:** Direct serving by FastAPI to minimize deployment complexity.
*   **Public Docs Publishing:** Markdown source files under `docs/access/site/` are rendered into checked-in static HTML docs pages by a lightweight Python generator (`scripts/build_public_docs.py`) and served through the same FastAPI/Vercel static path model as the marketing pages.

## 3. Database & Storage
*   **Primary Data:** **SQLite** (`data/markets.db`).
    *   Stores: All market data, outcomes, tags, and history.
    *   Mode: **Write-Ahead Logging (WAL)** enabled for high-performance concurrent read/write.
*   **Telemetry:** SQLite (`data/metrics.db`) for tracking request logs and performance.
*   **Note:** The backend relies *exclusively* on local SQLite for market queries. It does NOT connect to external databases for read operations.

## 4. External Integrations
*   **Core Data API:** **Polymarket Gamma API** used via a custom client (`gamma_client.py`).
*   **Blockchain Indexing:** **Goldsky Subgraph** for robust and low-latency holder data retrieval.
*   **Authentication:** **Supabase Auth** (Email/Google).
    *   Role: Strictly handles user identity and session management on the Frontend.
    *   Backend Interaction: The Python backend does not directly query Supabase. User features (like saved filters) are managed client-side or verified via tokens if needed in the future.
    *   Public Schema Role: Supabase `public` is limited to auth-adjacent user metadata (`profiles`) and lightweight marketing telemetry (`marketing_events`), protected by Row Level Security and written directly from the frontend.

## 5. Development & Deployment
*   **Containerization:** **Docker** and **Docker Compose** for environment consistency.
*   **Testing:** **pytest** and `unittest` for backend and API correctness. Includes `tests/rebuild_test_data.py` for generating integration test snapshots.
*   **E2E Testing/Automation:** **Playwright** (Python) for automated browser testing and demo asset generation.
*   **Reverse Proxy:** **Caddy** included in the production container setup.

---
*Updated: 2026-01-01 - Added Playwright to support automated demo asset generation and E2E testing.*
*Updated: 2026-03-10 - Documented the minimal Supabase public schema for auth profiles and marketing telemetry.*
*Updated: 2026-03-10 - Added markdown-driven public docs publishing via a custom Python generator for the multipage `/docs` surface.*
