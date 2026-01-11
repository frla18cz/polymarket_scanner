# Plán: Implementace Retry mechanismu pro HoldersClient

## Fáze 1: Implementace Logic
- [x] Task: Aktualizovat `HoldersClient` [commit: 82c16a9]
    - Upravit metodu `fetch_holders` v souboru `holders_client.py`.
    - Obalit volání `requests.get` do `for` cyklu (rozsah 3 pokusů).
    - Přidat `time.sleep(1)` v bloku `except`, pokud to není poslední pokus.
    - Přidat logování (`logger.warning`) při zachycení chyby před retry.
- [ ] Task: Conductor - User Manual Verification 'Implementace Logic' (Protocol in workflow.md)

## Fáze 2: Testování
- [ ] Task: Vytvořit Unit Test pro Retry
    - Vytvořit nový testovací soubor `tests/test_holders_retry_unittest.py` (nebo přidat do existujícího `test_holders_client_unittest.py`).
    - Použít `unittest.mock` pro simulaci selhání (side_effect=[Exception, Exception, Success]).
    - Ověřit, že metoda vrátí data i po 2 selháních.
    - Ověřit, že metoda vrátí prázdný list po 3 selháních.
- [ ] Task: Ověřit chování logování
    - Spustit test a zkontrolovat, zda se v konzoli/logu objevují varování o retry.
- [ ] Task: Conductor - User Manual Verification 'Testování' (Protocol in workflow.md)
