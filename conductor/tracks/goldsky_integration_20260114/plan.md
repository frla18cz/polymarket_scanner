# Plán implementace: Goldsky Subgraph Integration

Tento plán popisuje kroky pro integraci Goldsky Subgraph pro stahování držitelů, nahrazující/doplňující stávající limitované API.

## Fáze 1: Příprava a Konfigurace [checkpoint: 74938ff]
- [x] Úkol: Přidat `GOLDSKY_SUBGRAPH_URL` do environment proměnných (např. v `.env` nebo v kódu jako default). [b85935a]
- [x] Úkol: Vytvořit placeholder pro novou třídu `GoldskyClient` v `holders_client.py`. [b85935a]
- [~] Task: Conductor - User Manual Verification 'Fáze 1' (Protocol in workflow.md)

## Fáze 2: Testy a Core Logika (TDD)
- [ ] Úkol: Napsat unit test v `tests/test_goldsky_client_unittest.py` pro ověření komunikace se subgraph (mockování odpovědí).
- [ ] Úkol: Implementovat `GoldskyClient.fetch_holders_subgraph` s podporou pro:
    - GraphQL query (GetUserBalances).
    - Limit "Top 20" per outcome.
    - Retry logiku.
- [ ] Úkol: Ověřit, že testy procházejí.
- [ ] Task: Conductor - User Manual Verification 'Fáze 2' (Protocol in workflow.md)

## Fáze 3: Integrace do Scraperu
- [ ] Úkol: Upravit `smart_money_scraper.py` tak, aby prioritně volal `GoldskyClient`.
- [ ] Úkol: Implementovat logiku "Primary: Goldsky, Fallback: Legacy API" v `process_market_holders_worker`.
- [ ] Úkol: Ujistit se, že batch insert do SQLite funguje správně i pro nová data.
- [ ] Task: Conductor - User Manual Verification 'Fáze 3' (Protocol in workflow.md)

## Fáze 4: Verifikace a Cleanup
- [ ] Úkol: Spustit integrační testy a ověřit Smart Money výpočty.
- [ ] Úkol: Provést manuální scrape a zkontrolovat logs/data v DB.
- [ ] Task: Conductor - User Manual Verification 'Fáze 4' (Protocol in workflow.md)
