# Implementační plán: Fetch Top 20 Holders Per Outcome

## Fáze 1: Úprava klientů [checkpoint: 85f1d15]
- [x] Task: Analýza možností Goldsky Subgraph pro "Top N per Group". (Pokud nelze jedním dotazem, implementovat cyklus přes outcomes).
- [x] Task: Upravit `GoldskyClient.fetch_holders_subgraph` pro získání 20 holderů pro každý outcome.
- [x] Task: Upravit `HoldersClient.fetch_holders` (Legacy API fallback) pro získání adekvátního počtu dat.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) (85f1d15)

## Fáze 2: Verifikace scraperu
- [x] Task: Ověřit, že `smart_money_scraper.py` správně zpracovává a ukládá zvýšený objem dat.
- [x] Task: Spustit `tests/rebuild_test_data.py` a ověřit v DB, že existují trhy s > 20 holdery.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
