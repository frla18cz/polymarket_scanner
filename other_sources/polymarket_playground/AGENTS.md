# Repository Guidelines

## Project Structure & Module Organization
Core analytics live at the repository root: `events.py` captures active markets, `analyze_market_players.py` maps wallets to positions, `analyze_subgraph.py` fetches subgraph snapshots, and `aggregate_pnl.py` summarizes realized P/L. Targeted probes reside in `tests/` (`test_endpoint.py`, `test_single_wallet.py`, `test_subgraph_user.py`) and provide quick API checks. Generated CSV and JSON artifacts belong in `data/`; overwrite in place and keep bulky ad-hoc exports out of version control. Jupyter notebooks under `scripts/` document experiments—port durable logic back into Python modules for repeatable runs.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv .venv && source .venv/bin/activate`, then install dependencies via `pip install -r requirements.txt`. Refresh market snapshots through `python events.py`. Run `python analyze_market_players.py` once a snapshot exists to produce `data/market_players_analysis.csv` (use `--test` for a fast Top-10 dry run stored in `tests/output/`). Execute `python analyze_subgraph.py` to gather position data and follow with `python aggregate_pnl.py` to roll up wallet totals in `data/pnl_by_user.csv`.

## Coding Style & Naming Conventions
Target Python 3.10+, use four-space indentation, and declare shared options as `UPPER_SNAKE_CASE` constants near the top of each module. Name new files with descriptive `snake_case` identifiers. Prefer vectorized pandas operations and keep per-row loops guarded by comments explaining the trade-off. Log file destinations and record counts whenever a script writes artifacts so downstream analysts can trace outputs quickly.

## Testing Guidelines
Testing currently relies on deterministic script execution. Keep probes idempotent—handle missing files gracefully and short-circuit when APIs return empty data. When introducing a new analysis, extend a script under `tests/` or add a lightweight companion that prints a sample row and percentile metrics. For long pulls, expose pagination or limit arguments (e.g., the `--test` flag on analysis scripts) so contributors can run quick smoke passes before overnight jobs.

## Commit & Pull Request Guidelines
With no published history, adopt Conventional Commit prefixes (`feat:`, `fix:`, `docs:`) to keep the log searchable. Scope each commit to one pipeline or dataset adjustment and avoid committing large CSVs unless they are canonical fixtures. Pull requests should describe the affected data sources, list the commands executed, and attach before/after snippets from `data/*.csv`. Highlight any new external endpoints and summarize throttling assumptions in the PR body.

## Data & API Etiquette
Polymarket APIs enforce soft rate limits; retain batching, `time.sleep`, and useful logging when modifying fetch loops. Do not embed private keys or tokens—load secrets via environment variables and `python-dotenv` if secure configuration becomes necessary. Trim transient debug prints before submitting a change so stored analytics remain readable.
