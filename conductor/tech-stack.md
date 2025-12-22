# Technology Stack: PolyLab

## 1. Backend
*   **Language:** Python 3.12+
*   **Framework:** **FastAPI** for high-performance API endpoints and static file serving.
*   **Server:** **Uvicorn** as the ASGI web server.
*   **Data Validation:** **Pydantic** for schema enforcement and type safety.

## 2. Frontend
*   **Architecture:** Single-file Static HTML/JS.
*   **Framework:** **Vue.js** (CDN-hosted) for reactive UI components.
*   **Styling:** **Tailwind CSS** (CDN-hosted) for rapid UI development and styling.
*   **Strategy:** Direct serving by FastAPI to minimize deployment complexity.

## 3. Database & Storage
*   **Database:** **SQLite** (`data/markets.db`).
*   **Mode:** **Write-Ahead Logging (WAL)** enabled to support concurrent read/write operations (Scraper vs. API).
*   **Telemetry:** SQLite (`data/metrics.db`) for tracking request logs and performance.

## 4. External Integrations
*   **Core Data API:** **Polymarket Gamma API** used via a custom client (`gamma_client.py`).
*   **Authentication:** Supabase Auth (Email/Google) integration planned for premium features.

## 5. Development & Deployment
*   **Containerization:** **Docker** and **Docker Compose** for environment consistency.
*   **Testing:** **pytest** and `unittest` for backend and API correctness.
*   **Reverse Proxy:** **Caddy** included in the production container setup.
