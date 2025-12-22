# Initial Concept
PolyLab (Polymarket Scanner)

# Product Guide: PolyLab

## 1. Product Vision
PolyLab is a high-performance market scanner and analytics tool designed for **Polymarket** bettors, traders, and analysts. It bridges the gap between raw market data and actionable insights by providing a fast, filterable interface enriched with advanced metrics that are not readily available on the official Polymarket UI.

Unlike the standard interface, PolyLab prioritizes **speed of discovery** and **analytical depth**, enabling users to quickly identify betting opportunities based on calculated metrics like APR, spread, and liquidity. While currently operating on an hourly update cycle, it serves as a powerful companion tool for research and position scouting, specifically excluding high-frequency arbitrage strategies.

The project is currently free-to-use, with potential future plans for premium features. The immediate goal is to establish utility and value to support a grant application or partnership with Polymarket.

## 2. Target Audience
*   **Bettors & Traders:** Users looking for high-value positions based on fundamental analysis and market inefficiencies (excluding pure arbitrage).
*   **Analysts & Researchers:** Individuals monitoring market sentiment, probability trends, and liquidity across a broad range of events.

## 3. Core Features
*   **High-Performance Scanner:** A consolidated view of active markets, optimized for rapid scanning and sorting.
*   **Advanced Metrics:**
    *   **APR Calculation:** Annualized Percentage Rate estimates for market positions.
    *   **Spread Analysis:** Visibility into the bid-ask spread to assess trade costs.
    *   **Liquidity Tracking:** Liquidity metrics to gauge market depth.
*   **Granular Filtering:**
    *   **Time-based Filters:** Filter markets by start/end dates and duration.
    *   **Price Filters:** Narrow down opportunities by probability/price ranges.
    *   **Tag Management:** Powerful search using inclusion and exclusion tags to isolate specific niches.
*   **Data Aggregation:** Hourly snapshots of market data to provide a stable analysis baseline.

## 4. Technical Foundation
*   **Data Source:** Polymarket's **Gamma API**.
*   **Ingestion:** A dedicated ETL script (`scraper.py`) fetches and processes market data on an hourly schedule.
*   **Storage:** **SQLite** with Write-Ahead Logging (WAL) enabled, ensuring high performance and concurrency for read-heavy workloads.
*   **Architecture:** A Python-based backend (FastAPI) serving a lightweight, single-file frontend, optimized for deployment on VPS or containerized environments.
