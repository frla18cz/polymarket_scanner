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
- [x] Task: Conductor - User Manual Verification 'Phase 1: Metric Removal' (Protocol in workflow.md)

## Phase 2: Performance Optimization
Goal: Improve API response times by optimizing database queries and indices.

- [x] Task: Backend - Enhance Database Indices in `main.py`
    - Add `CREATE INDEX IF NOT EXISTS idx_amo_condition_id ON active_market_outcomes(condition_id)`.
    - Verify all filtered columns (`volume_usd`, `liquidity_usd`, `price`, `spread`, `apr`, `end_date`) have appropriate indices.
- [x] Task: Backend - Optimize `get_markets` Query [f6d3a2e]
- [x] Task: Conductor - User Manual Verification 'Phase 2: Performance Optimization' (Protocol in workflow.md)

## Phase 3: UI Stability
Goal: Prevent the UI from resetting state during auto-refresh.

- [x] Task: Frontend - Update `fetchMarkets` to preserve state [75d603a]
- [x] Task: Frontend - Synchronize `static/index.html` with `frontend_deploy/index.html` [75d603a]
- [x] Task: Conductor - User Manual Verification 'Phase 3: UI Stability' (Protocol in workflow.md)

[checkpoint: phase_3_complete]
