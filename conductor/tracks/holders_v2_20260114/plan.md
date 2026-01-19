# Plán: Holders Analysis V2 (Kategorizace, Řazení a Aliasy)

## Fáze 1: Analýza API a Schéma databáze [checkpoint: 7c24b0b]
- [x] Úkol: Analýza API pro získání aliasů [checkpoint: 7f3b891]
    - Note: Alias is available as `name` field in Legacy API (`/holders`). Goldsky Subgraph and PnL API do not provide it.
- [x] Úkol: Migrace databáze - přidání sloupce `alias` [checkpoint: 5a7c92b]
- [x] Úkol: Aktualizace Pydantic modelů [checkpoint: 5a7c92b]
- [x] Úkol: Conductor - User Manual Verification 'Analýza API a Schéma databáze' (Protocol in workflow.md)

## Fáze 2: Backend - Rozšíření Scraperu a API [checkpoint: 07919cd]
- [x] Úkol: Implementace získávání aliasů v `SmartMoneyScraper` [checkpoint: 191a9e2]
    - Upravit logiku stahování P/L tak, aby se ukládal i nalezený alias.
    - Zajistit, aby prázdné aliasy nepřepsaly již existující (pokud API vrátí null).
- [x] Úkol: Úprava API endpointu pro držitele [checkpoint: 7c24b0b]
    - Modifikovat `/api/markets/{id}/holders` tak, aby prováděl JOIN na `wallets_stats` a vracel `alias`.
- [x] Úkol: Testování Backend změn (TDD) [checkpoint: 7c24b0b]
    - Napsat testy pro ověření, že scraper správně ukládá aliasy.
    - Napsat testy pro ověření, že API endpoint vrací aliasy v JSON odpovědi.
- [x] Úkol: Conductor - User Manual Verification 'Backend - Rozšíření Scraperu a API' (Protocol in workflow.md)

## Fáze 3: Frontend - Kategorizace a Řazení [checkpoint: 8164c20]
- [x] Úkol: Rozdělení držitelů na Yes/No v UI [checkpoint: 8164c20]
- [x] Úkol: Implementace interaktivního řazení [checkpoint: 8164c20]
- [x] Úkol: Logika zobrazení Alias vs. Adresa [checkpoint: 8164c20]
- [x] Úkol: Testování Frontend změn [checkpoint: 8164c20]
- [x] Úkol: Conductor - User Manual Verification 'Frontend - Kategorizace a Řazení' (Protocol in workflow.md)

## Fáze 4: Finální verifikace a Dokumentace
- [x] Úkol: E2E testování celého procesu (Scrape -> DB -> API -> UI) [checkpoint: 8164c20]
- [x] Úkol: Aktualizace `docs/UI_CONTRACT.md` o nové parametry API [checkpoint: 8164c20]
- [x] Úkol: Conductor - User Manual Verification 'Finální verifikace a Dokumentace' (Protocol in workflow.md)
