# Specifikace: Validace, Zvýšený Limit a Retry pro Holders API

## Přehled
Polymarket API občas vrací neúplná data. Navíc, při malém limitu stahovaných záznamů může dojít k tomu, že minoritní strana (např. NO) se do výběru vůbec nedostane. Cílem je zajistit kompletní a validní data.

## Funkční požadavky
1.  **Zvýšení Limitu API:**
    - V `HoldersClient.fetch_holders` zvýšit parametr `limit` z 50 na **1000**.
    - Toto zajistí, že i při velké nerovnováze stran (např. 900 YES vs 50 NO) stáhneme dostatek dat pro obě strany.

2.  **Validace Odpovědi:**
    - Po stažení a zpracování dat (flattening) provést kontrolu.
    - **Podmínka:** Alespoň 20 unikátních holderů pro Outcome 0 (např. NO) A 20 unikátních holderů pro Outcome 1 (např. YES).
    - Tato podmínka se aplikuje na data získaná z API.

3.  **Retry Logika:**
    - Pokud podmínka validace není splněna, považuje se to za chybu stahování.
    - Čekat 2 sekundy a zkusit znovu.
    - Celkem 3 pokusy (1 hlavní + 2 retry).

4.  **Finální Akce (Při neúspěchu):**
    - Pokud se validace nezdaří ani po 3. pokusu: **Logovat varování a vrátit `None`**.
    - `None` signalizuje volajícímu kódu (scraperu), že data jsou nespolehlivá a trh má být přeskočen (aby nedošlo k přepsání existujících dat v DB neúplným snapshotem).

5.  **Finální Akce (Při úspěchu):**
    - Pokud se validace zdaří: Vrátit kompletní seznam stažených holderů (až 1000 záznamů).

## Kritéria přijetí
- Volání API používá `limit=1000`.
- Scraper neuloží data (přeskočí update), pokud nenajde alespoň 20 holderů na každé straně (po vyčerpání retry pokusů).
- Do databáze se ukládá širší spektrum holderů (vše co API vrátí do limitu 1000).
