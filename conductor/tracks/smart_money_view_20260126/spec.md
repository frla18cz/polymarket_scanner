# Specifikace Tracku: Smart Money View (Dominance ziskových holderů)

## 1. Přehled (Overview)
Cílem tohoto tracku je přidat do PolyLabu nové zobrazení "Smart Money", které uživatelům umožní rychle identifikovat markety, kde existuje výrazná převaha ziskových (profitable) holderů na jedné straně proti ztrátovým (losing) na straně druhé. Tento pohled bude sdílet filtry s hlavním scannerem, ale změní prezentaci dat pro zaměření na sentiment velkých/ziskových hráčů.

## 2. Funkční požadavky (Functional Requirements)
*   **Přepínač zobrazení:** V horní části aplikace (nad seznamem marketů) přibude přepínač mezi "Scanner" (standardní view) a "Smart Money" (nové view).
*   **Logika Smart Money:**
    *   Pro každý market se analyzují top holdeři obou stran (YES/NO).
    *   **Ziskový holder:** `total_pnl > profit_threshold` (default $1).
    *   **Ztrátový holder:** `total_pnl < 0`.
    *   **Dominance:** Výpočet převahy ziskových na jedné straně vs. ztrátových na protistraně.
*   **Nové filtry v sekci "Advanced":**
    *   `profit_threshold`: Minimální PnL pro označení holdera za "ziskového" (výchozí > 1).
    *   `min_profitable`: Minimální počet ziskových holderů na jedné straně (výchozí 10).
    *   `min_losing_opposite`: Minimální počet ztrátových holderů na protistraně (výchozí 15).
*   **UI v řádku marketu:**
    *   Nahrazení cenových sloupců za vizuálně bohaté "Smart Money Score".
    *   Zobrazení počtů (ziskoví/ztrátoví) s grafickým "boostem" (např. barevné bary, intenzita pozadí podle síly dominance).
    *   Jasné barevné odlišení YES (zelená) vs. NO (červená) strany.

## 3. Technické požadavky (Non-Functional Requirements)
*   **Výkon:** Výpočty dominance musí probíhat efektivně na frontendu z dat, která už API vrací (seznam holderů).
*   **Konzistence:** Při přepnutí pohledu musí zůstat zachovány všechny ostatní filtry (Search, APR, Tagy, Time).
*   **Responzivita:** Zobrazení musí být přehledné i na mobilních zařízeních (využití horizontálního scrollu nebo úprava šířky sloupců).

## 4. Akceptační kritéria (Acceptance Criteria)
*   [ ] Uživatel může jedním kliknutím přepnout na Smart Money view.
*   [ ] V Smart Money view jsou vidět počty ziskových/ztrátových holderů pro obě strany.
*   [ ] Strana s převahou je vizuálně zvýrazněna sytostí barvy úměrně k síle dominance.
*   [ ] Filtry v sekci "Advanced" správně omezují seznam zobrazených marketů v reálném čase.
*   [ ] API kontrakt zůstává nezměněn, využívají se stávající data o holderech.

## 5. Mimo rozsah (Out of Scope)
*   Změna frekvence scrapování dat (zůstává hodinová).
*   Historické grafy vývoje dominance (pouze aktuální snapshot).
