# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

# Project Overview
This repository contains tools to analyze Polymarket market data. It includes scripts to fetch active markets, map token holders, calculate P/L for wallets, and generate summary reports. The project is built with Python and pandas, designed for both data pipelines and ad-hoc analysis.

# Environment Setup

## Installation
1.  **Create and activate virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  **Install dependencies**:
    *   Core dependencies: `pip install -r requirements.txt`
    *   UI dependencies: `pip install -r requirements-ui.txt`

## Configuration
*   Secrets (private keys, tokens) must be loaded via environment variables using `python-dotenv`.
*   Create a `.env` file if necessary, but **never commit it**.

# Architecture & Structure

## Key Components
*   **Core Scripts (Root)**:
    *   `events.py`: Fetches active markets via Gamma API.
    *   `analyze_market_players.py`: Analyzes holders and calculates realized P/L per market.
    *   `analyze_subgraph.py`: Fetches global positions with P/L from Goldsky subgraph.
    *   `aggregate_pnl.py`: Aggregates P/L by user wallet.
    *   `final_analysis.py` & `debug_matching.py`: Detailed market analysis and debugging.
*   **Data (`data/`)**: Stores generated CSV/JSON artifacts. These are overwritten on each run.
*   **Tests (`tests/`)**: Contains standalone smoke test scripts (e.g., `test_endpoint.py`) and output from test runs.
*   **UI (`ui/`)**: Streamlit application for controlling the pipeline and visualizing results (`streamlit_app.py`).

## Data Flow
The typical data pipeline flows as follows:
1.  `events.py` -> Generates `data/markets_current.(json|csv)`
2.  `analyze_market_players.py` -> Generates `data/market_players_analysis.csv`
3.  `analyze_subgraph.py` -> Generates `data/subgraph_pnl_analysis.csv`
4.  `aggregate_pnl.py` -> Generates `data/pnl_by_user.csv`

# Common Development Tasks

## Running Analysis
*   **Refresh Markets**: `python events.py`
*   **Market Players Analysis**: `python analyze_market_players.py`
*   **Subgraph Analysis**: `python analyze_subgraph.py`
*   **Aggregate P/L**: `python aggregate_pnl.py`

## Testing & Debugging
*   **Smoke Tests**: Run standalone scripts in `tests/` to check API availability.
    ```bash
    python tests/test_endpoint.py
    ```
*   **Dry Run / Test Mode**: Most analysis scripts support a `--test` flag to limit execution (e.g., top 3 markets) and save output to `tests/output/`.
    ```bash
    python analyze_market_players.py --test
    python final_analysis.py --test --max-markets 5
    ```

## UI Development
*   **Start UI**:
    ```bash
    streamlit run ui/streamlit_app.py
    ```
*   The UI controls the pipeline and visualizes data from the `data/` directory.

# Lifecycle & Process

This project follows a strict data pipeline defined in [PROCESS.md](PROCESS.md).
The current state of the pipeline (last run times, stats) is tracked in `data/pipeline_state.json`.

Always check `pipeline_state.json` before running heavy operations to see if dependencies (e.g., a fresh snapshot) are met.

# Big Data Handling
When working with data in this project, be aware that datasets (especially subgraph exports) can be very large (GBs).

*   **No Full Loads**: Avoid `pd.read_csv('large_file.csv')` without `chunksize` or `nrows` limits. It will cause OOM crashes.
*   **Streaming/Chunking**: Use streaming patterns to process data iteratively.
    ```python
    with pd.read_csv(FILE, chunksize=100_000) as reader:
        for chunk in reader:
            process(chunk)
    ```
*   **Future Architecture**: We plan to migrate from CSV to a local OLAP database (DuckDB) to handle larger datasets efficiently.

# Coding Standards & Guidelines

## Style
*   **Python Version**: Target Python 3.10+.
*   **Formatting**: Use 4-space indentation.
*   **Naming**:
    *   New files: `snake_case` descriptive names.
    *   Constants: `UPPER_SNAKE_CASE` (near top of module).
*   **Performance**: Prefer vectorized pandas operations over row iteration. Comment loop trade-offs if necessary.

## Data & API
*   **Rate Limits**: Respect Polymarket API soft limits. Retain `time.sleep` and batching logic.
*   **Idempotency**: Scripts should handle missing files gracefully and short-circuit on empty API data.
*   **Logging**: Log file destinations and record counts when writing artifacts.
