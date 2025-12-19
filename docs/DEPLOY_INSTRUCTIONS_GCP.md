# Nasazení Polymarket Scanneru na Google Cloud (GCP)

Tento návod předpokládá, že máš vytvořenou VM instanci (např. e2-small) s OS Ubuntu nebo Debian.

## 1. Připojení k serveru
V Google Cloud Console klikni na tlačítko **SSH** vedle své instance.

## 2. Instalace Dockeru
Zkopíruj a spusť tyto příkazy (jeden po druhém):

```bash
# Aktualizace systému
sudo apt-get update

# Instalace Dockeru a Gitu
sudo apt-get install -y docker.io docker-compose-v2 git

# Přidání uživatele do skupiny docker (abys nemusel psát sudo před každým docker příkazem)
sudo usermod -aG docker $USER
```

*Po posledním příkazu může být nutné zavřít SSH okno a otevřít ho znovu, aby se změna skupiny projevila.*

## 3. Stažení a spuštění projektu

```bash
# 1. Naklonování repozitáře (nahraď URL svou adresou, nebo použij SCP pro nahrání souborů)
# Pokud nemáš veřejné repo, můžeš složku nahrát přes tlačítko "Upload File" v SSH okně (ozubené kolo vpravo nahoře).
# Předpokládejme, že jsi nahrál složku 'polymarket_scanner' do domovského adresáře.

cd polymarket_scanner

# 2. (Volitelné) Nastavení domény pro HTTPS
# Ověř Caddyfile; pro PolyLab typicky používáme API host (např. api.polylab.app).
# nano Caddyfile
# (Ctrl+O ulož, Ctrl+X konec)

# 3. Spuštění
docker compose up -d --build
```

## 4. Ověření
Aplikace by měla běžet na IP adrese tvé instance na portu 80 (pokud používáš Caddy) nebo 8000.
Otevři v prohlížeči: `http://TVOJE_EXTERNAL_IP:8000` nebo `https://api.polylab.app` (pokud máš DNS + HTTPS).

## 5. Správa
*   **Logy:** `docker compose logs -f`
*   **Restart:** `docker compose restart`
*   **Stop:** `docker compose down`
