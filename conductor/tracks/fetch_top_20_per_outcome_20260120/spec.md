# Specifikace: Fetch Top 20 Holders Per Outcome

## 1. Cíl
Zvýšit granularitu analýzy "Smart Money" tím, že budeme stahovat top 20 držitelů pro **každý možný výsledek** (outcome) trhu, nikoliv pouze 20 držitelů celkově. U binárních trhů (YES/NO) to znamená stažení až 40 držitelů (20 YES + 20 NO).

## 2. Současný stav
- `GoldskyClient` a `HoldersClient` limitují výsledek na 20 záznamů na trh (bez ohledu na outcome).
- To vede k tomu, že u trhů s dominantní stranou (např. 90% YES) můžeme ztratit informace o největších držitelích menšinové strany (NO).

## 3. Požadavky
- **GoldskyClient:** Upravit GraphQL dotaz nebo logiku zpracování tak, aby pro každé `outcomeIndex` v trhu vrátil top 20 držitelů.
- **HoldersClient (Legacy):** Pokud API podporuje filtrování podle outcome, iterovat přes outcome. Pokud ne, stáhnout větší batch a filtrovat lokálně.
- **Scraper:** Ujistit se, že `smart_money_scraper.py` správně uloží všechna data do DB (odstranění duplicit je již implementováno, ale je třeba ověřit limity).

## 4. Akceptační kritéria
- [ ] Pro binární trh (YES/NO) je v DB uloženo až 40 holderů (20 pro YES, 20 pro NO), pokud existují.
- [ ] Logika "Smart Money Win Rate" stále funguje (nyní bude mít přesnější data).
- [ ] Výkon scraperu není degradován o více než 2x (stahujeme 2x více dat).

## 5. Technické poznámky
- Pozor na "Multiple Choice" trhy, které mohou mít více outcomes. Limit 20 per outcome by mohl vést k velkému počtu záznamů. Zvážit globální limit (např. max 100 per market) nebo ponechat 20 per outcome (většina trhů má málo outcomes).
- Goldsky Subgraph umožňuje `orderBy` a `first`. Možná bude nutné poslat dotaz pro každý outcome zvlášť nebo použít komplexnější query.
