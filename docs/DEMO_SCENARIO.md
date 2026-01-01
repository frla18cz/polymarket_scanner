# PolyLab Demo Scenario

This document defines the standard scenario for generating product demos (video/GIF). Ideally, this scenario is automated via `generate_demo.py`.

## Scenario Steps

1.  **Initial State:** Start at the homepage with default filters.
2.  **Category Selection:**
    *   Locate "Include Categories".
    *   Click "ALL" to reset/ensure all are selected.
3.  **Expiration Filter:**
    *   Locate "Expires Within".
    *   Move slider or select preset for "30d" (End next month/30 days).
    *   Demonstrate "Not Sooner Than" staying at "Any" or "24h".
4.  **Price/Probability Range:**
    *   Locate "Outcome Price Range".
    *   Set Min to **90%** (Safe bets).
    *   Set Max to **99%**.
5.  **Constraints:**
    *   Set **Max Spread** to **2.0¢**.
    *   Set **Min Volume** to **$10k**.
    *   Set **Min Liquidity** to **$3k**.
6.  **Results:**
    *   Scroll to the table results.
    *   Hover over a row to show details (if applicable).

## Technical Requirements
*   **Resolution:** 1920x1080 (1080p) or 1280x720 (720p).
*   **Format:** MP4 (H.264) for high quality.
*   **Visuals:** Show smooth mouse movements and click indicators.
