# Specifikace: Smart Money Legacy Revert & Robust Retry

## Přehled
Tento track řeší návrat k "legacy" metodě stahování dat o držitelích (holders) a jejich aliasech v modulu `smart_money_scraper.py`. Cílem je dočasně vyřadit integraci s Goldsky Subgraph, kterou ponecháme zálohovanou pro budoucí použití, a implementovat robustnější systém pokusů (Second Pass), aby byla zajištěna maximální kompletnost dat při výpadcích nebo limitování API.

## Funkční požadavky
1.  **Odstranění Goldsky z ostrého provozu:**
    *   `GoldskyClient` bude přesunut z `holders_client.py` do nového souboru `other_sources/holders_client_goldsky_backup.py`.
    *   V `smart_money_scraper.py` bude odstraněna veškerá logika, která se pokouší o stahování dat přes Goldsky.
2.  **Výhradní použití Legacy API:**
    *   `SmartMoneyScraper` bude pro data o držitelích i aliasech používat pouze `HoldersClient` (endpoint `/holders`).
3.  **Implementace "Second Pass" (Druhý průchod):**
    *   Scraper bude sledovat ID trhů, u kterých se v prvním kole nepodařilo stáhnout data (např. kvůli timeoutu nebo 429).
    *   Po dokončení hlavní smyčky se scraper pokusí o "druhý průchod" pouze pro tato selhaná ID.
4.  **Konfigurace workerů:**
    *   Ponecháme nastavení `max_workers=10` pro paralelní zpracování, což je vyvážený kompromis pro stabilitu.

## Akceptační kritéria
- [ ] `smart_money_scraper.py` nepoužívá `GoldskyClient`.
- [ ] Existuje soubor `other_sources/holders_client_goldsky_backup.py` s funkčním původním kódem Goldsky klienta.
- [ ] Scraper po dokončení první fáze vypíše počet selhaných trhů a spustí pro ně druhý pokus.
- [ ] Testy ověřují, že se aliasy i držitelé stahují korektně z Legacy API.
