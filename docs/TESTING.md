# Testy a performance plán (Codex)

## Jak spustit testy nad hlavní DB

- Všechny testy (bez performance):
  - `python -m unittest discover -s tests -p "*_unittest.py"`
- Performance simulace (opt-in):
  - `RUN_PERF_TESTS=1 python -m unittest discover -s tests -p "*_unittest.py"`

Pozn.: V tomhle prostředí nepoužíváme `fastapi.testclient.TestClient` (nesedí verze `httpx`) ani nespouštíme lokální server (bind na socket je blokovaný), takže voláme přímo funkce endpointů v `main.py`.

## Testovací matrix (kombinace)

### A) “Stažení dat” (Gamma API) – unit testy s mockem
Soubor: `tests/test_gamma_client_unittest.py`

- **Pagination / offset**: `MarketFetcher.fetch_all_markets(limit=2)` načítá stránky, dokud není poslední stránka kratší.
- **Stop na prázdné dávce**: `MarketFetcher.fetch_all_events()` skončí při první prázdné odpovědi.
- **Retry logika**: `GammaClient.get_markets()` po chybě retry a nakonec uspěje (mock + `time.sleep` no-op).

### B) “Simulace uživatele” – kombinace filtrů (correctness)
Soubor: `tests/test_api_markets_unittest.py`

Scénáře odpovídající typickým akcím ve frontend UI. Vše běží nad snapshotem hlavní DB a tagy/termíny se berou dynamicky z DB (top tagy podle četnosti), aby testy držely i při změnách dat.

- **Excluded**: 1 tag a 2 tagy vyloučené.
- **Included**: 1 tag, 2 tagy a comma-separated vstup (`"tagA,tagB"`), jak to chodí z UI/proxy.
- **Included + Excluded konflikt**: `included=[A,B]` + `excluded=[A]` → výsledek je podmnožina `(B \\ A)`.
- **Price (pravděpodobnost)**: `min_price/max_price` kolem mediánu.
- **Spread**: `max_spread` kolem 25. percentilu.
- **Volume/Liquidity**: `min_volume/min_liquidity` kolem 75. percentilu.
- **Expirace**: `max_hours_to_expire` se volí tak, aby to mělo výsledky.
- **Search**: term se bere z existující otázky v DB.

### C) “Simulace uživatele” – performance (latence)
Soubor: `tests/test_perf_simulation_unittest.py`

- Testy jsou opt-in přes `RUN_PERF_TESTS=1`.
- Běží nad snapshotem hlavní DB (SQLite `backup()` do temp souboru, originál se nemění).
- Měří čas volání `get_markets(...)` pro typické scénáře:
  - **Excluded Crypto** (nejčastější)
  - **Included+Excluded + další filtry** (horší kombinace)

Volitelné budgety (když chceš hlídat regresi tvrdě, v ms):
- `PERF_BUDGET_EXCLUDED_SINGLE_MS`
- `PERF_BUDGET_EXCLUDED_MULTI_MS`
- `PERF_BUDGET_INCLUDED_MULTI_MS`
- `PERF_BUDGET_INCLUDED_CSV_MS`
- `PERF_BUDGET_INCLUDED_EXCLUDED_MS`
- `PERF_BUDGET_PRICE_RANGE_MS`
- `PERF_BUDGET_EXPIRING_SOON_MS`

Override cesty k hlavní DB (když je repo jinde):
- `MAIN_DB_PATH="/cesta/k/data/markets.db"`

