# Initial Concept
Polymarket market research, P/L analysis, and "smart money" identification.

# Product Guide

## Target Audience
- **Crypto Traders & Smart Money Trackers:** Individuals seeking actionable insights into market trends and profitable wallet behaviors.
- **Data Analysts & Developers:** Professionals interested in leveraging Polymarket's Gamma API and subgraph data for custom analysis and tool building.
- **Researchers:** Academics and industry experts studying prediction markets, user profitability, and behavioral patterns.

## Core Value Proposition
Polymarket Playground serves as a comprehensive toolkit for analyzing prediction market data. It bridges the gap between raw data and actionable intelligence by automating the ingestion of complex market events, calculating precise Profit & Loss (P/L) metrics, and scoring wallet performance. For traders, it unveils "Smart Money" movements; for analysts, it provides a robust pipeline and clean datasets; and for researchers, it offers a granular view into market mechanics.

## Key Features
- **Automated Data Pipeline:** seamless extraction of active markets, token holders, and user positions using Polymarket's Gamma API and Goldsky subgraph.
- **Advanced P/L Analysis:** Calculation of realized P/L, active positions, and historical performance for individual wallets.
- **Smart Money Identification:** a proprietary scoring system (Equity Scoring) that evaluates wallets based on equity smoothness, Sharpe ratio, and maximum drawdown to identify consistent performers.
- **Dual-Interface Visualization:**
    - A **Streamlit** app for quick, script-based exploratory data analysis.
    - A **Next.js Dashboard** for polished, interactive presentations of market analytics and wallet profiles.
- **Data Persistence & Management:** Efficient storage using DuckDB for analytical queries and CSV/JSON for accessible artifacts.

## Success Metrics
- **Data Integrity:** Accuracy of P/L calculations and consistency between API and subgraph data.
- **Pipeline Reliability:** ability to run end-to-end data ingestion and analysis without errors (handling API rate limits and missing data).
- **User Engagement:** adoption of the dashboard for monitoring market signals and wallet tracking.
