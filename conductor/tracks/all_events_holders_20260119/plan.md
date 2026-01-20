# Implementační plán: Robustní analýza holderů

## Fáze 1: Úprava klientů a scraperu [checkpoint: c278484]
- [x] Task: Odstranit validační limity v `holders_client.py` (v obou klientech: `HoldersClient` i `GoldskyClient`). (fd77284)
- [x] Task: Upravit `HoldersClient` tak, aby vracel nalezená data i při nízkém počtu (místo `None`). (fd77284)
- [x] Task: Zajistit, aby `GoldskyClient` i `HoldersClient` respektovaly limit 20 holderů na trh. (49b13b9)
- [x] Task: Verifikace scraperu `smart_money_scraper.py` - musí korektně zpracovat prázdné seznamy holderů bez chyb. (545c5e3)
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) (c278484)

## Fáze 2: API a Database Integrity
- [x] Task: Upravit SQL dotaz v `main.py` (endpoint `/api/markets`), aby explicitně nefiltroval NULL hodnoty u `smart_money_win_rate`. (d5ea876)
- [x] Task: Přidat unit test v `tests/test_api_markets_unittest.py` pro ověření přítomnosti trhů bez metrik. (d5ea876)
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Fáze 3: Testovací nástroje
- [ ] Task: Vytvořit skript `tests/rebuild_test_data.py` dle specifikace (fetch 100 markets + holders).
- [ ] Task: Dokumentovat použití skriptu v `tests/README.md` (nebo v existující dokumentaci).
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
