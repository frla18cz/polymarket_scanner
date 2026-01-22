# Implementation Plan: Deployment Prep & Smart Money Optimization

## Phase 1: Database Refactoring & API Integration [checkpoint: 7a8b9c0]
Cílem je oddělit Smart Money data do vlastní tabulky, aby byla nezávislá na častých aktualizacích základních dat trhu.

- [x] Task: Migrace databáze - vytvoření tabulky `market_smart_money_stats`
    - [x] Přidat definici tabulky do `scraper.py` (tak aby nebyla mazána při každém běhu) nebo do inicializační logiky v `main.py`.
    - [x] Tabulka bude obsahovat: `condition_id` (PK), `win_rate`, `last_updated_at`.
- [x] Task: Úprava `smart_money_scraper.py`
    - [x] Změnit cílovou tabulku pro ukládání win_rate z `active_market_outcomes` na `market_smart_money_stats`.
    - [x] Implementovat `INSERT OR REPLACE` logiku pro aktualizaci statistik.
- [x] Task: Úprava `scraper.py`
    - [x] Odstranit sloupec `smart_money_win_rate` z tabulky `active_market_outcomes` (protože bude v jiné tabulce).
    - [x] Ujistit se, že `setup_db` nemaže novou tabulku `market_smart_money_stats`.
- [x] Task: Úprava API v `main.py`
    - [x] Upravit SQL dotaz v endpointu `/api/markets` tak, aby prováděl `LEFT JOIN active_market_outcomes` s `market_smart_money_stats`.
    - [x] Ověřit, že API stále vrací stejnou strukturu JSON (aby se nerozbil frontend).
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Robust Scheduling & Docker configuration [checkpoint: 1d2e3f4]
Zajištění, aby skripty běžely automaticky ve správných intervalech bez kolizí.

- [x] Task: Implementace vylepšeného scheduleru v `auto_refresh.py`
    - [x] Přidat knihovnu `APScheduler` (pokud je dostupná) nebo robustní smyčku s podporou více úloh.
    - [x] Nastavit Job 1: `run_scrape()` každých 60 minut.
    - [x] Nastavit Job 2: `run_smart_money()` každých 6 hodin (360 minut).
- [x] Task: Docker Readiness & Logging
    - [x] Zkontrolovat `docker-compose.yml`, zda jsou správně namapovány `/app/data` a `/app/logs`.
    - [x] Ověřit restart policy (`unless-stopped`).
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: UI Enhancement & Data Freshness [checkpoint: 5g6h7i8]
Zobrazení informace o čerstvosti dat uživateli.

- [x] Task: API - Přidání časové značky aktualizace
    - [x] Přidat do `/api/markets` (nebo do nového meta-endpointu) čas poslední úspěšné aktualizace z tabulky `market_smart_money_stats`.
- [x] Task: Frontend - Zobrazení indikátoru
    - [x] Upravit `static/index.html` (a následně `frontend_deploy/index.html`), aby zobrazoval text: "Smart Money Analysis: [X] hours ago".
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Final Verification & Deployment [checkpoint: 9j0k1l2]
Celkové otestování systému v simulovaném produkčním prostředí.

- [x] Task: E2E Test v Dockeru
    - [x] Spustit `docker-compose up --build -d`.
    - [x] Ověřit logy obou služeb (`web` a `worker`).
    - [x] Ručně vyvolat Smart Money analýzu a ověřit promítnutí do UI.
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)