# Plán: Validace Holders a Zvýšení Limitu

## Fáze 1: Implementace Validace a Limitu
- [x] Task: Upravit `HoldersClient` - Limit [commit: d23b941]
    - Změnit defaultní `limit` v metodě `fetch_holders` na 1000.
- [x] Task: Upravit `HoldersClient` - Validace Logika [commit: d23b941]
    - Rozšířit stávající retry cyklus.
    - Uvnitř cyklu (po stažení dat) přidat kontrolu: Spočítat holdery pro každý `outcomeIndex` (0 a 1).
    - Pokud `count(outcome_0) < 20` NEBO `count(outcome_1) < 20`:
        - Logovat specifické varování: "Validation failed: Only X YES / Y NO holders found (attempt N/3)."
        - Vyvolat interní výjimku (nebo `continue`), aby se spustil retry `except` blok nebo další iterace.
- [x] Task: Upravit Návratovou Hodnotu při Selhání [commit: d23b941]
    - Pokud selžou všechny pokusy (síťová chyba nebo validace), metoda musí vrátit `None` (místo prázdného seznamu `[]`).
- [ ] Task: Conductor - User Manual Verification 'Implementace' (Protocol in workflow.md)

## Fáze 2: Update Scraperu
- [x] Task: Upravit `smart_money_scraper.py` [commit: d23b941]
    - Aktualizovat `process_market_holders_worker`:
        - Pokud `fetch_holders` vrátí `None`: Logovat varování ("Skipping market X - insufficient data") a vrátit prázdný seznam unikátních peněženek (aby se nepokračovalo v P/L fetchi pro tento trh).
        - **Důležité:** Neukládat nic do DB (`save_holders_batch` se nesmí zavolat), aby se nesmazala stará data.
- [ ] Task: Conductor - User Manual Verification 'Scraper Update' (Protocol in workflow.md)

## Fáze 3: Testování
- [ ] Task: Unit Testy Validace
    - Test: API vrátí 1000 záznamů, validace projde -> OK.
    - Test: API vrátí 10 záznamů (5 YES, 5 NO) -> Retry 3x -> Fail -> Return None.
    - Test: API vrátí data jen pro jednu stranu -> Retry 3x -> Fail -> Return None.
- [ ] Task: Conductor - User Manual Verification 'Testování' (Protocol in workflow.md)
