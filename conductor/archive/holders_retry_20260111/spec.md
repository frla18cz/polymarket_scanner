# Specifikace: Retry mechanismus pro HoldersClient

## Přehled
Cílem tohoto tracku je zvýšit robustnost stahování dat o držitelích (holders) přidáním mechanismu pro opakování požadavku (retry) v případě selhání. Aktuálně `fetch_holders` při jakékoliv chybě okamžitě selže a vrátí prázdný seznam, což znehodnocuje data při dlouhých bězích scraperu.

## Funkční požadavky
- Implementovat jednoduchou smyčku (loop) pro opakování požadavků v metodě `HoldersClient.fetch_holders`.
- Celkový počet pokusů: 3 (1 hlavní + 2 opakování).
- Časová prodleva mezi pokusy: Fixní 1 sekunda.
- Podmínka pro retry: Jakákoliv zachycená výjimka (`Exception`) během požadavku.
- Logování: Každý neúspěšný pokus musí být zalogován jako `warning` s informací o čísle pokusu. Finální selhání po 3 pokusech bude zalogováno jako `error`.

## Nefunkční požadavky
- Zachovat stávající návratový typ (seznam slovníků nebo prázdný seznam).
- Minimalizovat dopad na rychlost scraperu v případě, že API funguje správně.

## Kritéria přijetí
- Metoda `fetch_holders` se pokusí o stažení dat až 3x, pokud dojde k chybě.
- Pokud se stažení podaří na 2. nebo 3. pokus, data jsou normálně zpracována.
- Pokud selžou všechny 3 pokusy, metoda vrátí prázdný seznam `[]`.
- V logu jsou vidět záznamy o opakováních v případě simulovaného výpadku.

## Mimo rozsah (Out of Scope)
- Implementace exponenciálního backoffu (zvolena varianta A).
- Změny v `PnLClient` nebo jiných částech systému.
- Přidávání externích knihoven pro retry (např. tenacity).
