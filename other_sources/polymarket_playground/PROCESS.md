# Data Pipeline Process

This document defines the canonical data flow for the Polymarket Playground. It serves as the source of truth for understanding the lifecycle of data from ingestion to reporting.

## High-Level Overview

The pipeline consists of three main stages:
1.  **Ingestion (Stage 1)**: Fetching raw data from external APIs (Polymarket Gamma API, holders API).
2.  **Processing (Stage 2)**: Aggregating raw data into usable metrics (User P/L, Market stats).
3.  **Reporting (Stage 3)**: Visualizing results via UI or exporting CSVs.

```mermaid
graph TD
    A[Start] --> B[Stage 1A: Market Snapshot]
    B --> C[Stage 1B: Active Holders Snapshot]
    C --> D[Stage 2A: User P/L via user-pnl-api]
    D --> E[Stage 2B: Market Analysis]
    E --> F[Stage 3: Reporting/UI]
    B --> G[Stage 1C: Global Position Scan]
    G --> H[Stage 2A: User P/L Aggregation (Subgraph)]
    H --> E
```

## Stage Details

### Stage 1: Ingestion
*   **Step 1A: Market Snapshot**
    *   **Script**: `events.py`
    *   **Input**: Polymarket Gamma API
    *   **Output**: `data/markets_current.csv`
    *   **Description**: Fetches all active markets (IDs, Questions, Slugs, Liquidity).
*   **Step 1B: Active Holders Snapshot**
    *   **Script**: `fetch_active_holders.py`
    *   **Input**: Polymarket holders API
    *   **Output**: DuckDB `active_market_holders`
    *   **Description**: Fetches current holders for all active markets.
*   **Step 1C: Global Position Scan (Heavy)**
    *   **Script**: `analyze_subgraph.py` (with `--scan-all`)
    *   **Input**: Goldsky Subgraph
    *   **Output**: `data/subgraph_pnl_analysis.csv` (Raw Positions)
    *   **Description**: Downloads *all* user positions with non-zero P/L. This is a heavy operation (GBs of data).

### Stage 2: Processing
*   **Step 2A (Fast): User P/L via user-pnl-api**
    *   **Script**: `fetch_user_pnl_api.py`
    *   **Input**: `data/relevant_wallets.json` or DuckDB `active_market_holders`
    *   **Output**: `data/pnl_by_user_api.csv`
    *   **Description**: Fetches latest P/L per wallet from `user-pnl-api` (last data point).
*   **Step 2A (Subgraph): User Aggregation**
    *   **Script**: `aggregate_pnl.py`
    *   **Input**: `data/subgraph_pnl_analysis.csv`
    *   **Output**: `data/pnl_by_user.csv`
    *   **Description**: Sums realized P/L for every unique wallet. Uses chunked processing to handle large files.
*   **Step 2B: Final Market Analysis**
    *   **Script**: `final_analysis.py`
    *   **Input**: `data/markets_current.csv`, `data/pnl_by_user.csv` (or API)
    *   **Output**: `data/final_market_analysis.csv`, `data/detailed_market_analysis.csv`
    *   **Description**: Combines market data with user P/L to compute "Smart Money" metrics (e.g., how much profit the top holders on 'Yes' side have made historically).
*   **Step 2B (Smart Money Snapshot)**
    *   **Script**: `run_market_analysis.py`
    *   **Input**: `data/markets_current.csv`, DuckDB `active_market_holders`, P/L source:
        * Subgraph: `user_positions` (default)
        * API: `data/pnl_by_user_api.csv` (`--pnl-source api`)
    *   **Output**: `data/markets_analytics.csv`, DuckDB `market_analytics`
    *   **Description**: Snapshot of profitable holders per outcome.

### Stage 3: Reporting
*   **UI**: `ui/streamlit_app.py`
    *   Visualizes the artifacts generated in previous stages.
    *   **Note**: Do not load raw files from Stage 1B directly in the UI (OOM risk). Use Stage 2 outputs.

## State Management
The current state of the pipeline is tracked in `data/pipeline_state.json`.
This file records timestamps of the last successful run for each stage.

## Runtime Notes
To time the API-based P/L fetch, run a limited test:
```bash
time python fetch_user_pnl_api.py --limit 1000 --from-db
```
Use `--resume` to continue without re-fetching completed wallets.

**Example State:**
```json
{
  "last_run": {
    "snapshot": "2024-11-27T10:00:00Z",
    "ingestion": "2024-11-27T12:00:00Z",
    "aggregation": "2024-11-27T12:15:00Z"
  }
}
```
