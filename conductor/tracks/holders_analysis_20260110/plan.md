# Plan: Smart Money & Holders Analysis Implementation

## Phase 1: Database & Data Models
- [x] Task: Define SQL Schema [commit: dc5a115]
    - Create SQL migration script (or update schema definition logic) to add `holders` and `wallets_stats` tables.
    - Add necessary indices for performance (`market_id`, `wallet_address`).
- [x] Task: Update Database Initialization Logic [commit: dc5a115]
    - Modify `main.py` or `scraper.py` (wherever DB init happens) to ensure new tables are created on startup.
- [x] Task: Create Data Access Models (DTOs) [commit: dc5a115]
    - Define Pydantic models for `Holder` and `WalletStats` to ensure type safety within the Python code.

## Phase 2: Scraper Implementation (Holders & P/L) [checkpoint: 60d2108]
- [x] Task: Implement `HoldersClient` [commit: effae3c]
    - Add method to fetch holders from Gamma API with `limit=50`.
    - Implement the "sorted check" validation logic.
- [x] Task: Implement `PnLClient` [commit: effae3c]
    - Add method to fetch user P/L from the P/L API.
    - Implement concurrency logic (Worker Pool = 10, Sleep = 0.3s).
    - Implement retry logic for 429/timeouts.
- [x] Task: Create `SmartMoneyScraper` Job [commit: effae3c]
    - Create a new orchestration function/script that:
        1. Gets list of active markets.
        2. Iterates markets to fetch Holders.
        3. Extracts unique wallets.
        4. Fetches P/L for unique wallets.
        5. Saves data to SQLite.
- [x] Task: Conductor - User Manual Verification 'Scraper Implementation' (Protocol in workflow.md)

## Phase 3: Metrics Calculation & API Integration [checkpoint: ae94878]
- [x] Task: Implement Metrics Logic [commit: ae94878]
    - Create functions to calculate aggregated market metrics (e.g., `top_holders_win_rate`).
    - Update `get_markets` endpoint in `main.py` to join/include these new metrics in the response.
- [x] Task: Add Market Detail Endpoint [commit: ae94878]
    - Create a new API endpoint `/api/market/{id}/holders` (or expand existing detail endpoint) to return the Top-K holders list with their P/L data.
- [x] Task: Conductor - User Manual Verification 'Metrics Calculation & API Integration' (Protocol in workflow.md)

## Phase 4: Frontend Implementation [checkpoint: b1f5365]
- [x] Task: Update Scanner Table [commit: b1f5365]
    - Add new columns for "Smart Money" metrics to the main table.
    - Add sorting/filtering capabilities for these columns.
- [x] Task: Build Market Detail View [commit: b1f5365]
    - Create a UI component to display the list of Top Holders (address, size, P/L).
- [x] Task: Build Leaderboard Page [commit: b1f5365]
    - Create a simple "Smart Money Leaderboard" page listing top wallets by P/L.
- [x] Task: Conductor - User Manual Verification 'Frontend Implementation' (Protocol in workflow.md)

## Phase 5: Testing & Deployment [checkpoint: b1f5365]
- [x] Task: Write Unit Tests [commit: b1f5365]
    - Test Scraper logic (mock API responses).
    - Test Data Aggregation logic.
    - Test new API endpoints.
- [x] Task: Performance Verification [commit: b1f5365]
    - Run the scraper on a subset of data to verify rate limit adherence.
    - Check database query speeds with the new joins.
- [x] Task: Final Polish [commit: b1f5365]
    - Ensure UI is responsive and consistent.
    - Update documentation (`UI_CONTRACT.md`).
- [x] Task: Conductor - User Manual Verification 'Testing & Deployment' (Protocol in workflow.md)
