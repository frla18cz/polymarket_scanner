# Specification: Deployment Prep & Smart Money Optimization (2026-01-21)

## Overview
Cílem tohoto tracku je připravit aplikaci PolyLab na produkční provoz v Dockeru. Hlavní změny se týkají stability dat (oddělení Smart Money metrik do vlastní tabulky), robustního plánování úloh (1h pro ceny, 6h pro Smart Money) a vylepšení uživatelského rozhraní o informaci o čerstvosti dat.

## Functional Requirements
- **DB Refactoring (Option B):** 
    - Vytvořit novou tabulku `market_smart_money_stats` (primární klíč `condition_id`).
    - Upravit `smart_money_scraper.py`, aby ukládal výsledky (win rate) do této nové tabulky namísto přímého UPDATE v `active_market_outcomes`.
    - Upravit API v `main.py`, aby při dotazu na `/api/markets` provádělo `LEFT JOIN` na tuto novou tabulku.
- **Robust Scheduling:**
    - Upravit `auto_refresh.py` (nebo vytvořit nový `scheduler.py`), aby spouštěl:
        - `scraper.py` každou 1 hodinu.
        - `smart_money_scraper.py` každých 6 hodin.
    - Zajistit, aby tyto úlohy neběžely v kolizi (využití fronty nebo sekvenčního spouštění v rámci jednoho workeru).
- **UI Improvement (Option D):**
    - Do API odpovědi přidat pole s časem poslední úspěšné Smart Money analýzy.
    - Na frontend (`static/index.html`) přidat vizuální indikátor "Smart Money last updated: [timestamp]".

## Non-Functional Requirements
- **Docker Readiness:** Ujistit se, že `docker-compose.yml` správně mapuje logy a databáze a že se kontejnery po chybě restartují.
- **Data Integrity:** `scraper.py` může kdykoliv přepsat hlavní tabulku trhů, aniž by došlo ke smazání již vypočítaných Smart Money metrik.

## Acceptance Criteria
- [ ] `scraper.py` proběhne úspěšně a tabulka `active_market_outcomes` obsahuje čerstvá data (bez win_rate).
- [ ] `smart_money_scraper.py` zapíše data do `market_smart_money_stats`.
- [ ] API vrací spojená data (trhy + smart money win rate).
- [ ] Frontend zobrazuje čas poslední aktualizace Smart Money.
- [ ] Docker kontejnery `web` a `worker` běží stabilně.

## Out of Scope
- Implementace nových typů analýz (např. historie portfolia).
- Změna autentizační logiky (Supabase).
