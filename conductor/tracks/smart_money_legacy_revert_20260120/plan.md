# Plán: Smart Money Legacy Revert & Robust Retry

Tento plán popisuje kroky pro návrat k Legacy API pro stahování dat o držitelích a implementaci mechanismu "Second Pass" pro zajištění kompletnosti dat.

## Fáze 1: Záloha a pročištění kódu
- [~] Úkol: Záloha Goldsky klienta do `other_sources/holders_client_goldsky_backup.py`
- [ ] Úkol: Odstranění logiky pro Goldsky ze `smart_money_scraper.py` a `holders_client.py`
- [ ] Úkol: Aktualizace testů, které přímo závisely na Goldsky mockování v kontextu scraperu
- [ ] Task: Conductor - User Manual Verification 'Záloha a pročištění kódu' (Protocol in workflow.md)

## Fáze 2: Implementace robustního retrying (Second Pass)
- [ ] Úkol: Úprava `process_market_holders_worker` pro explicitní hlášení selhání (např. vracení None nebo výjimky)
- [ ] Úkol: Implementace logiky "Second Pass" v hlavní funkci `run()` pro trhy, které selhaly v prvním kole
- [ ] Úkol: Přidání detailnějšího logování pro proces retrying, aby bylo vidět, kolik trhů se podařilo "zachránit"
- [ ] Task: Conductor - User Manual Verification 'Robustní retrying' (Protocol in workflow.md)

## Fáze 3: Verifikace a kvalita
- [ ] Úkol: Spuštění integračních testů `test_smart_money_scraper_integration_unittest.py` a jejich případná úprava
- [ ] Úkol: Verifikační běh scraperu s nízkým limitem (např. `--limit 20`) pro ověření stability
- [ ] Task: Conductor - User Manual Verification 'Verifikace a kvalita' (Protocol in workflow.md)
