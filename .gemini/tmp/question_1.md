I'll now guide you through a series of questions to build a comprehensive specification (`spec.md`) for this track.

**Question 1:**
To ensure I target the correct code, I've identified two clients in `holders_client.py`:
1.  **Legacy:** `HoldersClient` (uses Polymarket `/holders` API).
2.  **New:** `GoldskyClient` (uses Goldsky Subgraph).

Currently, `smart_money_scraper.py` seems to try Goldsky first and falls back to Legacy, or uses Legacy to "enrich" missing aliases.

Is your goal to **completely stop using Goldsky** for now, and rely **exclusively on the Legacy `HoldersClient`** for fetching holders and aliases?

A) Yes, use Legacy only and disable Goldsky.
B) No, keep Goldsky for data but use Legacy only for aliases.
C) Type your own answer.