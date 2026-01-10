# Plan: Smart Money & Holders Analysis Implementation

## Phase 1: Database & Data Models
- [x] Task: Define SQL Schema [commit: dc5a115]
    - Create SQL migration script (or update schema definition logic) to add `holders` and `wallets_stats` tables.
    - Add necessary indices for performance (`market_id`, `wallet_address`).
- [x] Task: Update Database Initialization Logic [commit: dc5a115]
    - Modify `main.py` or `scraper.py` (wherever DB init happens) to ensure new tables are created on startup.
- [x] Task: Create Data Access Models (DTOs) [commit: dc5a115]
    - Define Pydantic models for `Holder` and `WalletStats` to ensure type safety within the Python code.

## Phase 2: Scraper Implementation (Holders & P/L)
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
- [ ] Task: Conductor - User Manual Verification 'Scraper Implementation' (Protocol in workflow.md)

## Phase 3: Metrics Calculation & API Integration
- [ ] Task: Implement Metrics Logic
    - Create functions to calculate aggregated market metrics (e.g., `top_holders_win_rate`).
    - Update `get_markets` endpoint in `main.py` to join/include these new metrics in the response.
- [ ] Task: Add Market Detail Endpoint
    - Create a new API endpoint `/api/market/{id}/holders` (or expand existing detail endpoint) to return the Top-K holders list with their P/L data.
- [ ] Task: Conductor - User Manual Verification 'Metrics Calculation & API Integration' (Protocol in workflow.md)

## Phase 4: Frontend Implementation
- [ ] Task: Update Scanner Table
    - Add new columns for "Smart Money" metrics to the main table.
    - Add sorting/filtering capabilities for these columns.
- [ ] Task: Build Market Detail View
    - Create a UI component to display the list of Top Holders (address, size, P/L).
- [ ] Task: Build Leaderboard Page
    - Create a simple "Smart Money Leaderboard" page listing top wallets by P/L.
- [ ] Task: Conductor - User Manual Verification 'Frontend Implementation' (Protocol in workflow.md)

## Phase 5: Testing & Deployment
- [ ] Task: Write Unit Tests
    - Test Scraper logic (mock API responses).
    - Test Data Aggregation logic.
    - Test new API endpoints.
- [ ] Task: Performance Verification
    - Run the scraper on a subset of data to verify rate limit adherence.
    - Check database query speeds with the new joins.
- [ ] Task: Final Polish
    - Ensure UI is responsive and consistent.
    - Update documentation (`UI_CONTRACT.md`).
- [ ] Task: Conductor - User Manual Verification 'Testing & Deployment' (Protocol in workflow.md)
