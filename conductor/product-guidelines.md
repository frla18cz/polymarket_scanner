# Product Guidelines: PolyLab

## 1. Voice and Tone
*   **Professional & Analytical:** Use direct, data-driven language. Avoid marketing hype or language typical of high-stakes gambling.
*   **Objective:** Present metrics as calculated data points. Ensure the user understands that these are analytical tools, not financial advice.
*   **Precise:** Use specific terminology (e.g., "Liquidity Depth," "Bid-Ask Spread," "Annualized Percentage Rate") consistently across the UI and documentation.

## 2. Design Philosophy
*   **Data Density:** Prioritize showing as much relevant information as possible in a single view without cluttering. Table-based layouts are preferred for the scanner.
*   **Performance First:** The UI must feel instantaneous. Filtering and sorting should happen client-side whenever possible to ensure a "zero-latency" user experience.
*   **Clarity over Decoration:** Use minimalist design elements. Icons and colors should serve a functional purpose (e.g., red/green for price movements, badges for categories) rather than just aesthetics.
*   **Dark Mode Optimization:** Given the trading/crypto context, the primary interface should be optimized for dark mode to reduce eye strain during long research sessions.

## 3. Metric Transparency
*   **Estimation Warnings:** Clearly label calculated metrics like APR as "Estimates" or "Projected."
*   **Data Freshness:** Always display the timestamp of the last data sync prominently, so users are aware of the hourly update cycle.
*   **Calculation Methodology:** Maintain a "Help" or "Info" section explaining exactly how APR, spread, and other custom metrics are derived from the Gamma API data.

## 4. User Experience (UX)
*   **Frictionless Exploration:** Users should be able to apply and clear multiple filters with single clicks.
*   **Mobile Research:** While the desktop view is for "power scanning," the interface must remain functional and readable on mobile devices for bettors checking markets on the move.
*   **Persistent State:** Where possible, remember user filter preferences or provide "Shareable URLs" that encode the current filter state.

## 5. Quality Standards
*   **Data Accuracy:** Accuracy of the scraper is the highest priority. Silent failures in data ingestion are unacceptable; errors must be logged and monitored.
*   **Backend Efficiency:** Optimize SQLite queries using appropriate indices to ensure the API remains fast as the database grows.
