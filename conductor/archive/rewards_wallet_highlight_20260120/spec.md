# Specifikace: Zvýraznění Rewards/System Peněženek

## Cíl
Identifikovat a vizuálně odlišit "systémové" peněženky (např. Liquidity Providers, Rewards kontrakty, UMA) v seznamu držitelů. Tyto peněženky často drží obrovské pozice ve většině trhů, což může běžného uživatele mást, pokud si myslí, že jde o "Smart Money" tradera.

## Analýza Dat
Z analýzy 100 trhů vyplývá, že adresa `0xa5ef39c3d3e10d0b270233af41cac69796b12966` figuruje v 82 % trhů s objemem řádově převyšujícím ostatní.
- **Adresa:** `0xa5ef39c3d3e10d0b270233af41cac69796b12966`
- **Typ:** Pravděpodobně System/Rewards/LP.

## Požadavky

### Backend & Databáze
1.  **Rozšíření DB:** Přidat do tabulky `wallets_stats` sloupec `tags` (TEXT/JSON) nebo `flags` pro označení typu peněženky.
2.  **Identifikace:** Vytvořit migrační skript nebo logiku, která označí známou adresu `0xa5ef...` tagem `REWARDS` nebo `SYSTEM`.
3.  **API:** Endpoint `/api/markets/{id}/holders` musí vracet tento tag/flag v objektu holdera.

### Frontend
1.  **Vizualizace:** V tabulce `Holders` (Desktop i Mobile) přidat u takto označené adresy ikonku (např. `ph-info`, `ph-robot` nebo `ph-bank`).
2.  **Tooltip:** Po najetí myší (nebo kliknutí na mobilu) zobrazit vysvětlení:
    > "This appears to be a system wallet (Liquidity Provider or Rewards Contract), not an individual trader."
3.  **Styl:** Může být mírně odlišena barvou (např. šedá/tlumená), aby tolik "nesvítila" mezi tradery.

## Akceptační Kritéria
- [ ] Adresa `0xa5ef...` má v API response příznak `is_system_wallet` (nebo tag).
- [ ] V UI se u této adresy zobrazuje informační ikona s tooltipem.
- [ ] Ostatní adresy (např. `cigarettes`) zůstávají bez změny.
