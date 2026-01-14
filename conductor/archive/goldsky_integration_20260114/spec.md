# Specifikace: Integrace Goldsky Subgraph pro stahování Holderů

## Přehled
Současná metoda stahování držitelů (holders) přes standardní API Polymarketu je často nespolehlivá (rate-limity). Tento track implementuje novou metodu využívající Goldsky Subgraph, která umožňuje stahovat data o držitelích pro všechny outcome indexy daného marketu. Pro optimalizaci a konzistenci budeme stahovat Top 20 držitelů pro každý outcome.

## Funkční požadavky
- **Nový Goldsky Client:** Implementace klienta pro komunikaci s Goldsky GraphQL endpointem.
- **Konfigurace:** URL endpointu bude konfigurovatelná přes proměnnou prostředí `GOLDSKY_SUBGRAPH_URL`.
- **Integrace do Smart Money Scraperu:** Úprava `smart_money_scraper.py` tak, aby prioritně používal Goldsky metodu. Původní metoda zůstane jako fallback.
- **Zpracování dat:**
    - Stahování **Top 20** držitelů pro každý outcome (Yes/No/atd.).
    - Dávkové ukládání (Batch Insert) do SQLite pro zachování výkonu.
- **Paralelizace:** Zachování/optimalizace ThreadPoolExecutoru pro rychlé stahování napříč markety.

## Nefunkční požadavky
- **Výkon:** Proces nesmí zablokovat databázi (použití WAL módu).
- **Stabilita:** Implementace retry logiky pro síťové chyby.
- **Kódový styl:** Striktní dodržení stávajících konvencí (Python type hints, logging, `logging_setup.py`).

## Akceptační kritéria
- [ ] Funkční `GoldskyClient`, který vrací Top 20 držitelů pro zadané `condition_id`.
- [ ] `smart_money_scraper.py` úspěšně naplní tabulku `holders` daty z Goldsky.
- [ ] Ověření, že data odpovídají očekávanému formátu pro výpočet Smart Money metrik.
- [ ] Úspěšné proběhnutí testů.

## Mimo rozsah (Out of Scope)
- Migrace historických dat o holderech.
- Stahování více než 20 držitelů na outcome (pokud to nebude vyžádáno později).
