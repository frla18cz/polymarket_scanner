# Specification: UI Stability, Performance & Metric Cleanup

## 1. Overview
This track addresses UI state preservation issues, performance bottlenecks in market filtering/sorting, and the removal of the Smart Money Win Rate metric.

## 2. Functional Requirements

### 2.1 UI Stability (Auto-refresh Fix)
- Prevent the frontend from resetting filters, sorting, and pagination (offset) when background data refreshes occur.
- Ensure the "auto-refresh" logic updates the data in place without destroying the current user view.

### 2.2 Performance Optimization
- Optimize the `get_markets` query in `main.py`.
- Identify and add missing SQLite indices for columns added in recent "Holders" tracks (e.g., fields related to smart money, holder counts, or specific outcome metrics).
- Target: Reduce filtering/sorting latency from 1-3s to < 200ms.

### 2.3 Metric Removal (Smart Money Win Rate)
- **Frontend**: Remove the "Smart Money Win Rate" column/metric from the market list and detail views.
- **Backend**: Remove the calculation and inclusion of Win Rate metrics from the API response to reduce computation and payload size.

## 3. Acceptance Criteria
- [ ] UI state (filters, sorting, pagination) persists after a data refresh.
- [ ] Market list filtering and sorting respond in < 200ms.
- [ ] "Smart Money Win Rate" is no longer visible in the application.
- [ ] Database indices are automatically created/verified on startup in `main.py`.

## 4. Out of Scope
- Refactoring the Win Rate calculation (this will be handled in a future track).
- Adding new filtering features.
