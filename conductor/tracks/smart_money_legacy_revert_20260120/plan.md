# Plán: Smart Money Legacy Revert & Robust Retry [checkpoint: f158d82]

Tento plán popisuje kroky pro návrat k Legacy API pro stahování dat o držitelích a implementaci mechanismu "Second Pass" pro zajištění kompletnosti dat.

## Fáze 1: Záloha a pročištění kódu [checkpoint: f158d82]
- [x] Úkol: Záloha Goldsky klienta do `other_sources/holders_client_goldsky_backup.py` [f158d82]
- [x] Úkol: Odstranění logiky pro Goldsky ze `smart_money_scraper.py` a `holders_client.py` [f158d82]
- [x] Úkol: Aktualizace testů, které přímo závisely na Goldsky mockování v kontextu scraperu [f158d82]
- [x] Task: Conductor - User Manual Verification 'Záloha a pročištění kódu' (Protocol in workflow.md) [f158d82]

## Fáze 2: Implementace robustního retrying (Second Pass) [checkpoint: f158d82]
- [x] Úkol: Úprava `process_market_holders_worker` pro explicitní hlášení selhání (např. vracení None nebo výjimky) [f158d82]
- [x] Úkol: Implementace logiky "Second Pass" v hlavní funkci `run()` pro trhy, které selhaly v prvním kole [f158d82]
- [x] Úkol: Přidání detailnějšího logování pro proces retrying, aby bylo vidět, kolik trhů se podařilo "zachránit" [f158d82]
- [x] Task: Conductor - User Manual Verification 'Robustní retrying' (Protocol in workflow.md) [f158d82]

## Fáze 3: Verifikace a kvalita [checkpoint: f158d82]
- [x] Úkol: Spuštění integračních testů `test_smart_money_scraper_integration_unittest.py` a jejich případná úprava [f158d82]
- [x] Úkol: Verifikační běh scraperu s nízkým limitem (např. `--limit 20`) pro ověření stability [f158d82]
- [x] Task: Conductor - User Manual Verification 'Verifikace a kvalita' (Protocol in workflow.md) [f158d82]