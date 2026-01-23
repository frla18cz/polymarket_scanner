# Implementation Plan: UI Stability, Performance & Metric Cleanup

This plan addresses the identified UI stability issues, performance bottlenecks, and the removal of the Smart Money Win Rate metric.

## Phase 1: Metric Removal (Smart Money Win Rate)
Goal: Clean up the codebase by removing the Smart Money Win Rate metric from the backend and frontend.

- [x] Task: Backend - Remove Smart Money Win Rate from `main.py` [92561a2]
    - Remove the `LEFT JOIN market_smart_money_stats` from the `get_markets` query.
    - Remove `min_smart_money_win_rate` filter parameter from `get_markets`.
    - Update the API response model to exclude the win rate field.
- [x] Task: Frontend - Remove Smart Money Win Rate UI from `index.html` [05d6f13]
    - Remove the "Smart Money Win Rate" slider filter from the sidebar.
    - Remove the "Smart Win" column from the desktop table header and rows.
    - Remove the Win Rate display from the mobile card view.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Metric Removal' (Protocol in workflow.md)

## Phase 2: Performance Optimization
Goal: Improve API response times by optimizing database queries and indices.

- [ ] Task: Backend - Enhance Database Indices in `main.py`
    - Add `CREATE INDEX IF NOT EXISTS idx_amo_condition_id ON active_market_outcomes(condition_id)`.
    - Verify all filtered columns (`volume_usd`, `liquidity_usd`, `price`, `spread`, `apr`, `end_date`) have appropriate indices.
- [ ] Task: Backend - Optimize `get_markets` Query
    - Review the generated SQL to ensure it uses indices efficiently.
    - Ensure the `WHERE` clauses for `end_date` (expiration) use optimal SQLite date/time comparisons.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Performance Optimization' (Protocol in workflow.md)

## Phase 3: UI Stability
Goal: Prevent the UI from resetting state during auto-refresh.

- [ ] Task: Frontend - Update `fetchMarkets` to preserve state
    - Modify `fetchMarkets` in `index.html` to accept an option to preserve the current `offset` and `expandedId`.
    - Update the `setInterval` refresh logic to call `fetchMarkets` with the "preserve state" flag.
    - Ensure that a "silent" refresh doesn't trigger a full-page loading overlay if possible.
- [ ] Task: Frontend - Synchronize `static/index.html` with `frontend_deploy/index.html`
    - Ensure both files are byte-identical as per project conventions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: UI Stability' (Protocol in workflow.md)

[checkpoint: phase_3_complete]
