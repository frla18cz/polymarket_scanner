# Specifikace: Holders Analysis V2 (Kategorizace, Řazení a Aliasy)

## 1. Přehled
Tento track vylepšuje stávající analýzu držitelů (Holders Analysis) o přehlednější zobrazení v UI, možnost interaktivního řazení a nahrazení anonymních adres čitelnými aliasy uživatelů z Polymarketu.

## 2. Funkční požadavky

### 2.1 Backend a Scraper
- **Analýza API:** Identifikovat v Polymarket API (pravděpodobně v endpointu pro profil uživatele nebo v detailech držitelů) pole pro alias (např. `displayName`, `proxyTitle` nebo `username`).
- **Aktualizace DB:** Rozšířit tabulku `wallets_stats` o sloupec `alias` (TEXT).
- **Rozšíření Scraperu:** Upravit `SmartMoneyScraper` tak, aby při zjišťování P/L peněženky zároveň uložil/aktualizoval její alias, pokud je dostupný.
- **API Endpoint:** Endpoint `/api/markets/{id}/holders` musí nově vracet pole `alias` pro každou peněženku.

### 2.2 Uživatelské rozhraní (Frontend)
- **Kategorizace Yes/No:** V detailu trhu rozdělit seznam držitelů do dvou jasně oddělených tabulek/sekcí: "Holders: YES" a "Holders: NO".
- **Interaktivní řazení:** 
    - Implementovat klikatelné hlavičky sloupců v obou tabulkách.
    - Podporovat řazení podle **Size** (velikost pozice) a **Total P/L** (celkový zisk/ztráta peněženky).
- **Zobrazení aliasů:** 
    - Pokud je pro peněženku dostupný alias, zobrazit jej místo adresy.
    - Pokud alias není, zobrazit zkrácenou adresu (např. `0x123...abcd`).
    - Původní celá adresa by měla zůstat dostupná (např. v atributu `title` pro zobrazení po najetí myší).

## 3. Akceptační kritéria
- [ ] Detail trhu zobrazuje dvě samostatné tabulky pro Yes a No držitele.
- [ ] V tabulkách je možné řadit kliknutím na záhlaví sloupců (Size, P/L).
- [ ] Uživatelé s nastaveným profilem na Polymarketu se zobrazují pod svým jménem (aliasem).
- [ ] Scraper korektně ukládá aliasy do databáze při každém běhu.
- [ ] API vrací aliasy společně s daty o držitelích.

## 4. Mimo rozsah (Out of Scope)
- Ruční editace aliasů v aplikaci (přebírají se pouze z Polymarketu).
- Historie změn aliasů (ukládá se vždy pouze ten nejnovější).
