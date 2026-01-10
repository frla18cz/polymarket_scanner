# Product Guidelines

## Presentation Style
- **Data-First & Objective:** The core value lies in the accuracy and clarity of the data. Interfaces should prioritize raw metrics, sortable tables, and minimalist, high-contrast charts. Avoid unnecessary clutter that distracts from the numbers.
- **Narrative & Insight-Driven:** While data comes first, use brief, punchy labels (e.g., "Whale Alert", "Smart Money") to draw attention to significant findings.
- **Visual & Interactive:** Use color-coding (Green/Red for P/L) and heatmaps to allow for rapid scanning of market states. Drill-down capabilities should be intuitive for deeper investigation.

## Tone and Voice
- **Energetic & Action-Oriented:** The platform operates in the fast-paced world of prediction markets. The language should be concise, active, and focused on "now."
- **Direct & Efficient:** Avoid jargon where simple terms suffice, but do not dumb down technical concepts. Assume the user is here to make decisions.
- **Alert-Driven:** Highlight changes and opportunities immediately.

## Design Principles
- **Speed is a Feature:** Dashboards must load fast, and scripts should be optimized for performance. Latency in data delivery reduces value.
- **Trust through Transparency:** Where possible, link back to source data (on-chain transactions, specific market IDs) to build confidence in the derived metrics.
- **Modular & Scriptable:** The design should encourage users to run their own analyses. Code should be clean, well-documented, and easy to extend.

## Data Handling
- **Precision:** P/L calculations must be exact. Rounding should be consistent and clearly indicated.
- **Freshness:** Timestamp everything. Users need to know exactly when the data snapshot was taken.
- **Privacy:** While analyzing public wallet data, avoid aggregating PII unless it is publicly associated with the wallet address.
