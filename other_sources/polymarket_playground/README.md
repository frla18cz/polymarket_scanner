# Polymarket Playground

## Přehled projektu
Repozitář slouží k průzkumu a analýze dat z trhů Polymarketu. Najdete zde skripty, které stahují otevřené trhy, mapují držitele tokenů, počítají P/L jednotlivých peněženek a vytvářejí souhrnné reporty. Vše je stavěné na Pythonu a pandas, takže je práce vhodná do datové pipeline i k ad-hoc průzkumům.

## Struktura repozitáře
- `events.py` – stáhne aktuálně otevřené trhy přes Gamma API a uloží je do `data/markets_current.(json|csv)`.
- `analyze_market_players.py` – pro každý trh získá držitele, spočítá jejich realizované P/L a vytvoří `data/market_players_analysis.csv`.
- `analyze_subgraph.py` – vytáhne z Goldsky subgrafu všechny pozice s nenulovým P/L a uloží je do `data/subgraph_pnl_analysis.csv`.
- `fetch_user_pnl_api.py` – rychlý fetch P/L přes `user-pnl-api` (poslední bod); ukládá `data/pnl_by_user_api.csv`.
- `aggregate_pnl.py` – agreguje výsledky peněženek z předchozího kroku do `data/pnl_by_user.csv`.
- `final_analysis.py` a `debug_matching.py` – doplňkové skripty pro hlubší analýzu jednoho trhu nebo pro ladění shody mezi trhem a P/L výstupy.
- `run_market_analysis.py` – Smart Money analýza nad `active_market_holders` + historickým P/L; ukládá long data do DuckDB `market_analytics` a generuje wide CSV `data/markets_analytics.csv` (Yes/No na jednom řádku; ostatní outcomes se ukládají jen v DB).
- `tests/test_endpoint.py`, `tests/test_single_wallet.py`, `tests/test_subgraph_user.py` – rychlé smoketesty API.
- `doc/` – pracovní návrhy dokumentace; oficiální popisy jsou součástí tohoto README.
- `scripts/` – Jupyter notebooky s experimenty; pokud z nich vzejde stabilní logika, přepište ji zpět do `.py` skriptů.
- `data/` – artefakty skriptů (CSV/JSON). Při opakovaném spuštění se přepisují.

## Nastavení prostředí
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Pro běh skriptů stačí Python 3.10+ a internetové připojení. Pokud budete používat soukromé klíče či tokeny, načtěte je z `.env` souboru přes `python-dotenv`.

## Typický workflow
1. Aktualizujte snapshot trhů: `python events.py`.
2. Získejte P/L pro držitele jednotlivých trhů: `python analyze_market_players.py`.
3. Stáhněte globální pozice ze subgrafu: `python analyze_subgraph.py`.
4. Agregujte P/L po peněženkách: `python aggregate_pnl.py`.
5. (Volitelné) Pro detailní pohled na konkrétní trh spusťte `python final_analysis.py` nebo `python debug_matching.py` s upravenou konfigurací.
6. Smart Money snapshot: `python run_market_analysis.py` (agreguje aktuální držitele s historickým P/L, ukládá long form do DuckDB + wide CSV).

### Alternativní rychlý P/L (user-pnl-api)
Pokud nepotřebujete subgraph a chcete rychlý snapshot P/L jako na profilu:
1. Aktualizujte snapshot trhů: `python events.py`.
2. Stáhněte držitele aktivních trhů do DB: `python fetch_active_holders.py`.
3. Načtěte P/L přes `user-pnl-api`: `python fetch_user_pnl_api.py --from-db`.
4. Spusťte Smart Money snapshot nad CSV: `python run_market_analysis.py --pnl-source api --pnl-csv data/pnl_by_user_api.csv`.

## Equity křivky a skóre
- Nově ve složce `equity_analysis/` (kód + výstupy). Příklad běhu z DuckDB: `python equity_analysis/equity_scoring.py --duckdb data/polymarket.db --db-query "SELECT updated_at as timestamp, user_addr as wallet_address, realizedPnl/1e6 as pnl FROM user_positions WHERE user_addr='0x908355107b56e0a66b4fd0e06b059899aec8d27b' ORDER BY updated_at" --min-points 2 --preview 5`.
- Alternativně SQLite (`--sqlite ...`) nebo CSV: `python equity_analysis/equity_scoring.py --input equity_analysis/data/user_transactions.csv --wallet-col wallet --ts-col timestamp --pnl-col pnl_delta --resample D`.
- Pro jiné DB URL (Postgres apod.) je k dispozici `--db-url` (vyžaduje ručně doinstalovat `sqlalchemy` + driver).
- Výpočet: kumulativní equity per wallet, metriky smoothness (net_change/total_variation), max drawdown, Sharpe z krokových návratností; skóre `0.45*smoothness + 0.35*sharpe - 0.20*max_drawdown`.
- Výstup: `equity_analysis/output/equity_scores.csv` seřazené podle skóre; parametry `--min-points`, `--preview`, `--resample`, `--limit` pro úpravu chování.

## Výstupy a interpretace
Výsledky leží vždy v `data/` a z názvu souboru je patrné, odkud pocházejí. Doporučujeme po každém běhu zkontrolovat počet řádků a datum generování, aby bylo jasné, ke kterému snapshotu se data vztahují. Logy z API volání se vypisují na standardní výstup.

## Testování a ladění
Smoketesty v `tests/test_*.py` prověřují dostupnost API a základní výpočty P/L. Přidáváte-li nové skripty, vytvořte obdobný lehký test (např. pro jedno tržiště) a držte kód idempotentní – musí zvládnout chybějící soubory i prázdné odpovědi. Pro rychlé ověření hlavních analýz využijte přepínač `--test`, který omezí počet trhů a uloží výsledky do `tests/output/`. Další procesní doporučení najdete v `AGENTS.md`.

## Poznámky k API
Polymarket API mají měkké limity, proto ponechte `time.sleep` intervaly a batche tak, jak jsou. V případě rychlého experimentu můžete limity snížit přes parametry skriptů, ale na produkční běhy je vraťte zpět. Nikdy neukládejte citlivé údaje do repozitáře; použijte proměnné prostředí.

## Smart Money (run_market_analysis.py)
- Vstupy: `data/markets_current.csv` (snapshot trhů), DuckDB tabulky `active_market_holders` (aktuální držitelé), `user_positions` (historický realized P/L), volitelně `wallet_labels`.
- Výstup: 
  - CSV `data/markets_analytics.csv` (wide, 1 řádek = 1 market, pouze Yes/No sloupce: `smart_holders_yes/no`, `smart_vol_yes/no`, `smart_ratio_yes/no`, `total_holders_yes/no`, `total_vol_snapshot_yes/no`, `outcome_price_yes/no` + metadata).
  - Tabulka `market_analytics` v `data/polymarket.db` (long form, 1 řádek = 1 outcome) pro SQL dotazy a multi‑outcome trhy.
- Klíčové sloupce v long formě (DB): `market_id`, `question`, `slug`, `outcome_label`, `outcome_index`, `smart_vol` (objem profitabilních peněženek), `smart_holders_count` (počet profitabilních peněženek na dané straně), `smart_ratio` (= smart_vol / total_vol_snapshot), `total_vol_snapshot`, `total_holders_count`, `liquidity_usd`, `volume_usd`, `market_snapshot_at`, `outcome_price` (aktuální cena outcome z `outcomePrices`), `event_link`, `snapshot_ts`.
- Spuštění: `python run_market_analysis.py` (předtím aktualizujte snapshot trhů a stáhněte držitele do `active_market_holders`).
- Rychlý P/L přes API: `python run_market_analysis.py --pnl-source api --pnl-csv data/pnl_by_user_api.csv`.
- Interpretace: „smart“ = peněženky s kladným historickým realized P/L. Multi‑outcome trhy mají více řádků dle `outcome_label` (např. Yes/No nebo roky).

## Final Market Analysis — parametry a metriky

Spuštění:
- Plný běh: `python final_analysis.py` (výstupy do `data/`)
- Rychlý běh: `python final_analysis.py --test --max-markets 5` (výstupy do `tests/output/`)
- Úprava koše: `python final_analysis.py --top-k 20 --min-position 50`

Parametry (platí i pro `analyze_market_players.py` pokud je uvádí):
- `--test` spustí omezený běh na prvních N trzích a ukládá do `tests/output/` (default: vypnuto; N=3).
- `--max-markets <N>` počet trhů v test módu (default: 3).
- `--top-k <K>` kolik peněženek na každé straně zahrnout (default: 10).
- `--min-position <X>` minimální velikost pozice pro zařazení do Top‑K (default: 0). Jednotka je buď USD (pokud endpoint vrátí `usdValue/value`), nebo počet shares (pokud je k dispozici jen `amount/balance`).
- `--output`, `--detail-output` (jen `final_analysis.py`) umožní přesměrovat cesty výstupů.

Slovníček metrik (CSV `final_market_analysis*.csv`):
- `yes_bettor_count`, `no_bettor_count`: počet peněženek v Top‑K koši na každé straně (Yes/No).
- `yes_profitable_bettors`, `no_profitable_bettors`: kolik z těchto peněženek má historicky kladný realizovaný P/L (> 0).
- `yes_total_pnl`, `no_total_pnl`: součet historického realizovaného P/L (USD) pro Top‑K peněženky na dané straně.
- `yes_weighted_avg_pl`, `no_weighted_avg_pl`: vážený průměr P/L, váha = `position_size` (aktuální velikost pozice z holders API). Vzorec: sum(P/L × size) / sum(size).
- `yes_median_pl`, `no_median_pl`: medián P/L v rámci Top‑K; méně citlivý na extrémy.
- `yes_topk_share_coverage`, `no_topk_share_coverage`: pokrytí objemu — podíl, kolik z celkových shares na straně drží Top‑K. Vzorec: `topk_total_shares / total_shares`. Prakticky: > 0.8 znamená, že Top‑K zachycuje většinu expozice.
- `yes_topk_total_shares`, `no_topk_total_shares`: součet shares u Top‑K peněženek.
- `yes_total_shares`, `no_total_shares`: celkové shares na straně dle holders API (včetně peněženek mimo Top‑K).

Slovníček pojmů:
- Top‑K: K největších peněženek na straně (seřazené podle `position_size`).
- `position_size`: velikost pozice peněženky na daném trhu; preferujeme `usdValue/value`, jinak `amount/balance/shares`. Jednotka se může lišit dle dostupných polí.
- `wallet_total_pl_usd`: historický realizovaný P/L (USD). Ze subgrafu konvertujeme z pevné škály (1e6) na USD; z `data-api/closed-positions` přichází přímo v USD.
- `outcomeIndex`: index strany — binární trhy mapujeme 0=Yes, 1=No.
- Shares: množství outcome tokenů; není vždy 1:1 s USD hodnotou.

Interpretace a limity:
- Pokud coverage klesá pod ~0.5, zvažte zvýšení `--top-k` nebo uvolnění `--min-position`.
- Velký rozdíl mezi váženým průměrem a mediánem značí „velrybí“ vliv.
- Analýza cílí primárně na binární trhy (Yes/No). U vícevýsledkových trhů je třeba kód rozšířit o další strany.

## UI — ovládání (Streamlit)

Je k dispozici jednoduché UI nad celým pipeline, které umožňuje:
- spustit stažení aktivních trhů (events.py)
- stáhnout P/L pozice ze subgrafu s limitem stránek (analyze_subgraph.py)
- agregovat P/L za peněženky (aggregate_pnl.py)
- spustit obě analytiky (analyze_market_players.py, final_analysis.py) se všemi hlavními parametry

Spuštění UI:
```bash
streamlit run ui/streamlit_app.py
```
V levém panelu nastavíte `Top-K`, `Min. position`, `Test mód` a parametry pro subgraph (počet stránek/velikost stránky). Tlačítka v hlavní části vždy spustí příslušnou část pipeline a níže zobrazí log výstup a náhled na výsledné CSV.

- **Rychlý refresh trhů (Krok 1A)**: tlačítko spouští `events.refresh_active_markets_snapshot()`, které pouze aktualizuje `data/markets_current.csv/json` a do každého řádku přidá `snapshot_fetched_at`. Běh je rychlý a nezasahuje do P/L pipeline; stávající výsledky zůstávají, dokud je nespustíte znovu v krocích 1B–1C a 2.
- **Prohlížení (Krok 3)**: tabulka „Final Analysis“ automaticky připojí k výsledkům likviditu (`liquidity_usd`), objem (`volume_usd`), klikací odkaz na event a sloupec `market_snapshot_at` s časem posledního fetchování. Díky tomu lze kombinovat starší P/L analýzu s aktuálním snapshotem trhů bez opětovného výpočtu.
- Nové trhy se v reportech objeví až po plném běhu analýzy; do té doby uvidíte jen metadata pro již dříve zpracované `market_id`.

## UI — návrh a doporučení

Cíl UI
- Rychle procházet trhy, filtrovat, a vidět Top‑K metriky (coverage, vážený průměr, medián) a detail peněženek bez ruční práce s CSV.

Varianty
- Streamlit (MVP v repu):
  - Plusy: čistý Python, rychlé prototypování, cachování (`st.cache_data`), snadné nasazení interně.
  - Mínusy: omezenější custom UX, méně vhodné pro složité role a routing.
- Plotly Dash:
  - Plusy: větší kontrola nad layoutem, bohaté grafy.
  - Mínusy: více boilerplate než Streamlit.
- Next.js + FastAPI (produkční stack):
  - Plusy: plná flexibilita, škálovatelnost, API kontrakty.
  - Mínusy: vyšší čas na první hodnotu, dva stacky.

Doporučený MVP (Streamlit)
- Přehled trhů: tabulka `markets_current.csv`, vyhledávání, filtry (aktivní, kategorie), timestamp snapshotu, tlačítko „Refresh snapshot“ (volá `events.py`).
- Detail trhu: graf coverage (gauge/bar), srovnání `weighted_avg_pl` vs. `median_pl`, tabulky Top‑K (Yes/No) s `position_size` a odkazem na peněženku.
- Detail peněženky: historický `wallet_total_pl_usd` z agregátů, jednoduchý přehled pozic (pokud dostupné).
- Ovládací panel: `TOP_K`, `MIN_POSITION`, přepínač `TEST_MODE` (pouští `final_analysis.py --test`).

Technické poznámky
- Nezatěžovat UI dlouhými běhy: v UI používat test mód, plné běhy spouštět separátně (cron/CLI). V UI číst výsledky z `data/` nebo `tests/output/`.
- Cachování: `st.cache_data(ttl=300)` pro CSV a subgraph dotazy, ať se UI chová svižně.
- Závislosti: doporučuji přidat volitelný `requirements-ui.txt` (`streamlit`, `plotly`).

Navržené kroky
1) Scaffold `ui/streamlit_app.py` s kartami Markets / Market detail / Wallet detail.
2) Datová vrstva (`services/data_loader.py`): funkce pro načítání CSV a (volitelně) bezpečné volání API s rate‑limitem.
3) Integrace metrik z `final_analysis.py` (čtení výstupů, ne runtime výpočty).
4) UX leštění: export CSV, per‑market parametry `TOP_K`, `MIN_POSITION`.

Otázky na upřesnění
- Preferuješ rychlý MVP ve Streamlitu, nebo rovnou robustní Next.js + FastAPI?
- Má UI spouštět dlouhé analýzy (batch), nebo jen prezentovat existující výstupy?
- Máme cílit na interní nástroj (firemní VPN) nebo veřejný přístup?

### Spuštění UI (MVP)
- Instalace: `pip install -r requirements.txt`
- Start: `streamlit run ui/streamlit_app.py`
- Sidebar obsahuje ovládání batch běhů (snapshot, Analyze Market Players, Final Analysis) a parametry (`TEST_MODE`, `MAX_MARKETS`, `TOP_K`, `MIN_POSITION`).
