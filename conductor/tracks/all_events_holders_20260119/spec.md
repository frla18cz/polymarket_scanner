# Specifikace: Robustní analýza holderů pro všechny trhy

## 1. Přehled
Cílem tohoto úkolu je zajistit, aby PolyLab zpracovával a zobrazoval všechny trhy bez ohledu na počet jejich holderů. Současná implementace vyřazuje trhy, které mají méně než 20 holderů pro "YES" nebo "NO" výsledky. Nově budeme brát v potaz všechny trhy (0 až 20 holderů) a zajistíme, aby se v UI zobrazovaly korektně i s neúplnými daty. Zároveň vytvoříme testovací skript pro stabilní vývoj.

## 2. Funkční požadavky
- **Odstranění validačních limitů:** Scraper nesmí zahodit trh, pokud má málo holderů. Jakýkoliv počet (i 0) je validní.
- **Limitace na Top 20:** Pro každý trh budeme stahovat a analyzovat maximálně 20 největších holderů.
- **Transparentní metriky:** Pokud trh nemá žádné holdery nebo data o jejich P/L, metrika `smart_money_win_rate` zůstane `NULL`.
- **API viditelnost:** API nesmí automaticky skrývat trhy s `smart_money_win_rate IS NULL`. Tyto trhy budou viditelné, dokud uživatel nepoužije explicitní filtr na minimální win rate.
- **Testovací skript:** Nový modul `tests/rebuild_test_data.py` umožní stáhnout 100 trhů a jejich kompletní data (holders + P/L) do lokálního snapshotu pro účely testování.

## 3. Akceptační kritéria
- [ ] Soubor `holders_client.py` neobsahuje podmínku vyžadující minimálně 20+20 holderů.
- [ ] Scraper `smart_money_scraper.py` úspěšně uloží data i pro trhy s např. 1 holderem.
- [ ] API v `main.py` vrací trhy s `smart_money_win_rate = null` v základním výpisu.
- [ ] Skript `tests/rebuild_test_data.py` je funkční a vytvoří validní testovací data.
- [ ] Unit testy ověřují, že trhy s 0 holdery nezpůsobí pád systému.

## 4. Mimo rozsah
- Úprava grafického designu UI (pouze zajistíme zobrazení dat).
- Integrace jiných zdrojů dat než Goldsky a Polymarket API.
