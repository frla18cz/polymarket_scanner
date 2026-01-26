# Specification: Smart Money & Holders Analysis

## 1. Overview
The "Smart Money & Holders Analysis" feature aims to enhance PolyLab's market evaluation capabilities by identifying and analyzing the top holders for each market. By correlating large positions with the historical performance (P/L) of those wallets, we can provide users with "Smart Money" sentiment metrics, helping them identify markets where successful traders are heavily positioned.

## 2. Functional Requirements

### 2.1 Data Ingestion (Scraper)
- **Schedule:** Runs every 6 hours (independent of the hourly price scraper).
- **Holders Collection:** 
    - Request endpoint: `https://data-api.polymarket.com/holders?market=<conditionId>&limit=50` (Targeting Top 20 + buffer).
    - **Validation Mechanism:** Check if the response items are strictly sorted by `position_size` descending.
        - *If Sorted:* Proceed with selecting Top 20.
        - *If Unsorted:* Log a warning.
    - Extract `wallet_address`, `outcome_index`, and `position_size`.
- **Top-K Selection:**
    - For each `outcome_index` within a market, select the top 20 holders by `position_size`.
- **P/L Analysis:**
    - For each unique wallet address found in the Top-K selection, fetch their P/L history via: `https://user-pnl-api.polymarket.com/user-pnl?user_address=<wallet_address>`.
    - Use the last data point `p` as the current P/L value.
- **Concurrency & Rate Limiting:**
    - Use a worker pool of 10 workers.
    - Implement a 0.3s sleep interval between requests to maintain ~19 req/s (below the 20 rps limit).
    - Implement retry logic (max 5 attempts) for failed requests (429s or timeouts).

### 2.2 Database Updates
- **New Table `holders`:** Store `market_id`, `outcome_index`, `wallet_address`, `position_size`.
- **New Table `wallets_stats`:** Store `wallet_address`, `total_pnl`, `last_updated`.
- **Market Metrics:** Aggregate data into the main `markets` table or a separate `market_analytics` table:
    - `top_holders_win_rate_index_<n>`: Percentage of top holders with positive P/L for outcome `n`.
    - `smart_money_sentiment`: A derived score based on volume-weighted P/L of holders.

### 2.3 User Interface
- **Scanner (Main View):** Add columns/filters for Smart Money metrics (e.g., "Top Holders P/L > 0%").
- **Market Detail View:** Display a table of Top-K holders per outcome, showing their address, position size, and total P/L.
- **Leaderboard:** A new page listing the top-performing wallets identified across all scanned markets.

## 3. Non-Functional Requirements
- **Performance:** DB queries for the main scanner must remain sub-second despite the additional metrics. Indices must be added for `wallet_address` and `market_id`.
- **Reliability:** The scraper must handle network errors gracefully and resume if interrupted.

## 4. Acceptance Criteria
- [ ] Scraper successfully fetches holders and P/L data without triggering permanent rate limits.
- [ ] Database correctly stores and associates P/L data with wallets.
- [ ] API provides market metrics based on holder data.
- [ ] Frontend displays Top Holders in the market detail view.
- [ ] Frontend allows filtering the scanner by at least one "Smart Money" metric.

## 5. Out of Scope
- Real-time P/L tracking (updates are every 6 hours).
- Tracking every holder (limited to top 1000 for collection, top 20 for metrics).
- Detailed trade history for each wallet.
