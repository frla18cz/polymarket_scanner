# Implementační plán: Smart Money View

Tento plán popisuje kroky pro implementaci nového zobrazení "Smart Money", které vizualizuje dominanci ziskových holderů na základě stávajících dat.

## Fáze 1: Příprava a filtry (Backend & State)
V této fázi připravíme logiku pro nové filtry a zajistíme, aby frontend správně pracoval s přepínáním stavů.

- [ ] Task: Update `UI_CONTRACT.md` – Dokumentace nových parametrů filtrů a chování Smart Money view.
- [ ] Task: Frontend State – Přidání stavu `currentView` (scanner/smart) a nových filtrů do Vue instance.
- [ ] Task: Backend Filters – Úprava `main.py` (get_markets) pro podporu nových query parametrů (`profit_threshold`, `min_profitable`, `min_losing_opposite`).
- [ ] Task: TDD – Vytvoření testu `tests/test_api_smart_money_filters_unittest.py` pro ověření funkčnosti filtrů na backendu.
- [ ] Task: Conductor - User Manual Verification 'Fáze 1: Příprava a filtry' (Protocol in workflow.md)

## Fáze 2: UI Struktura a Přepínač
Vytvoření vizuálních prvků pro přepínání pohledů a integrace nových filtrů do UI.

- [ ] Task: View Toggle – Implementace přepínače v horní části scanneru (Scanner vs. Smart Money).
- [ ] Task: Advanced Filters UI – Přidání inputů pro Smart Money filtry do sekce "Advanced" filtrů.
- [ ] Task: Conditional Column Rendering – Úprava šablony seznamu marketů, aby se sloupce měnily na základě `currentView`.
- [ ] Task: Conductor - User Manual Verification 'Fáze 2: UI Struktura' (Protocol in workflow.md)

## Fáze 3: Logika a Vizuální "Boost" Smart Money
Implementace výpočtů dominance a grafického znázornění v řádcích.

- [ ] Task: Dominance Logic – Implementace frontendové funkce pro výpočet ziskových/ztrátových z pole `top_holders`.
- [ ] Task: Smart Money Row Component – Vytvoření vizuálně bohatého zobrazení pro řádek v pohledu Smart Money.
    - Implementace barevných indikátorů (progress bary / intenzita pozadí).
    - Zobrazení počtů "P" (Profitable) a "L" (Losing).
- [ ] Task: TDD – Vytvoření testu `tests/test_ui_smart_money_logic_unittest.py` (Playwright) pro ověření správného výpočtu dominance na frontendu.
- [ ] Task: Styling Polish – Jemné ladění Tailwind tříd pro "boosted" vzhled (stíny, přechody, čitelnost).
- [ ] Task: Conductor - User Manual Verification 'Fáze 3: Vizuální Boost' (Protocol in workflow.md)

## Fáze 4: Finální verifikace a čištění
- [ ] Task: Mobile Optimization – Kontrola zobrazení na mobilních zařízeních, zajištění čitelnosti nových sloupců.
- [ ] Task: Performance Check – Ověření, že výpočty na frontendu nezpomalují plynulost scrollování při velkém počtu marketů.
- [ ] Task: Final Documentation – Aktualizace `README.md` nebo `GEMINI.md` o nové funkcionalitě.
- [ ] Task: Conductor - User Manual Verification 'Fáze 4: Finální verifikace' (Protocol in workflow.md)
