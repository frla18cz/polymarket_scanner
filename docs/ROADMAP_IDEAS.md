# 🚀 Polymarket Scanner: Masterplan & Roadmap

Tento dokument slouží jako strategický plán pro rozvoj projektu **Polymarket Scanner**. Cílem je transformovat tento nástroj z jednoduchého prohlížeče dat na komplexní **Intelligence Platform**, která dává traderům informační převahu.

---

## 🎯 Vize: Od "Data Viewer" k "Alpha Tool"
Náš cíl není jen zobrazovat, co se děje (to dělá Polymarket web), ale **odhalovat příležitosti**, které nejsou na první pohled vidět (arbitráže, mispricings, news sentiment) a doručovat je uživateli v reálném čase.

---

## 🗺️ Fáze 1: Data & Stabilita (Okamžité kroky)
*Cíl: Mít nejrychlejší a nejpřesnější data, robustní backend.*

- [x] **Standalone Architektura:** Oddělení od původního repozitáře (Hotovo).
- [x] **WAL Mód (SQLite):** Zajištění, že se DB nezamyká při čtení/zápisu (Hotovo).
- [ ] **Asynchronní Scraper (Turbo Mode):** Přepsat `scraper.py` z `requests` na `aiohttp`.
    *   *Dopad:* Zkrácení času aktualizace z ~50s na ~5-10s. Umožní "Near Real-time" data.
- [ ] **Historická Data:** Začít ukládat snapshoty cen v čase (nejen přepisovat aktuální stav).
    *   *Dopad:* Umožní vykreslovat grafy a analyzovat trendy ("Tento trh skočil o 20% za poslední hodinu").

---

## 🤖 Fáze 2: AI Integrace (The "Wow" Factor)
*Cíl: Využít LLM k pochopení kontextu trhu. Zde je největší potenciál pro získání Grantu od Polymarketu.*

### A. AI News Analyst ("Proč se to hýbe?")
*   **Koncept:** Uživatel vidí trh, který se propadl. Klikne na "Analyze with AI".
*   **Technika:** Backend vezme otázku trhu -> prohledá NewsAPI/Google -> předhodí titulky LLM -> LLM vyplivne shrnutí.
*   **Výstup:** "Trh klesl, protože SEC právě oznámil žalobu na tuto firmu."
*   **Náročnost:** Střední.

### B. Smart Auto-Tagging (Mikro-kategorie)
*   **Problém:** Polymarket má hrubé kategorie ("Crypto", "Politics").
*   **Řešení:** LLM projde názvy trhů a vytvoří dynamické tagy.
*   **Příklad:** `Will BTC hit 100k?` -> Tagy: `#Bitcoin`, `#PriceAction`, `#HighVol`.
*   **Dopad:** Mnohem lepší filtrování pro uživatele.

### C. Sentiment Indikátor
*   **Koncept:** Automatické skóre (0-100) vedle trhu, které ukazuje sentiment na sociálních sítích (Twitter/X, Farcaster).
*   **Hodnota:** Kontrariánské obchodování (když je sentiment super high, ale cena stagnuje -> Sell).

---

## 💰 Fáze 3: Finanční Nástroje & Notifikace
*Cíl: Nástroje, které přímo vydělávají peníze (nebo šetří čas).*

### A. Arbitrážní Scanner (Negative Risk) 💎
*   **Koncept:** Matematická jistota zisku. Polymarket má trhy s více výsledky.
*   **Logika:** Sečíst ceny všech outcomes v jednom eventu. Pokud `Suma < 1.00` (např. 0.98), nákupem všech pozic máš garantovaný zisk 2% (minus poplatky).
*   **Zobrazení:** Velký alert v dashboardu nebo speciální sekce "Free Money".

### B. Telegram Bot (Pasivní příjem) 🔔
*   **Koncept:** Uživatel nemusí sedět u PC.
*   **Funkce:** Bot pošle zprávu do kanálu, když:
    1.  Objeví se "Safe Haven" (>98% pravděpodobnost) s expirací do 24h.
    2.  Objeví se Arbitráž.
    3.  Velryba (Whale) nakoupí za více než $50k.
*   **Monetizace:** Freemium model (Zpožděné alerty zdarma, instantní za poplatek).

### C. Whale Watcher (Sledování velryb) 🐋
*   **Koncept:** Kdo hýbe trhem?
*   **Funkce:** Seznam "Top Holders" u každého trhu. Identifikace "Smart Money" peněženek (těch, co mají historicky vysoký zisk).

---

## 🚀 Fáze 4: Go-to-Market & Strategie
*Cíl: Získat uživatele, reputaci a financování.*

1.  **Public Deployment:**
    *   Nasadit na levný VPS (Hetzner/DigitalOcean) + Cloudflare.
    *   Doména: `polylab.app` nebo `polymarket-tools.com`.

2.  **Community Launch:**
    *   Sdílet na Discordu Polymarketu.
    *   Twitter vlákno s ukázkou "Jak jsem našel 5% ROI za den pomocí tohoto nástroje".
    *   Tagovat `@Polymarket`, `@VitalikButerin` (často o Polymarketu píše).
    *   **TODO:** Generate high-quality 1080p demo video (Current version in `generate_demo.py` needs better smoothness and clarity).

3.  **Grant Application:**
    *   Až bude mít projekt trakci (uživatele), požádat o grant.
    *   **Argument:** "Přináším vám likviditu a vzdělávám uživatele. Podpořte vývoj AI funkcí."

---

## 🛠️ Technický "Backlog" (Co zlepšit pod kapotou)

- [ ] **Filtrování systémových adres:** Automaticky ignorovat adresy jako "Polymarket: Rewards" při výpočtu Smart Money Win Rate (evidováno v `docs/DATA_ANOMALIES.md`).
- [ ] **Docker Compose:** Plná kontejnerizace (Server + Scraper + DB).
- [ ] **API Rate Limiting:** Ochrana vlastního API před přetížením.
- [ ] **Mobile UI:** Optimalizace dashboardu pro telefony (teď je to spíše desktop tabulka).
- [ ] **Unit Testy:** Abychom nerozbili filtry při dalších úpravách.

---

*Tento dokument byl vygenerován 5.12.2025 jako základní stavební kámen pro další vývoj.*

