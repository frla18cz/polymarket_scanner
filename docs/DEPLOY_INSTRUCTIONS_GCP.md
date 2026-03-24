# Nasazení Polymarket Scanneru na Google Cloud (GCP)

Tento návod předpokládá, že máš vytvořenou VM instanci (např. e2-small) s OS Ubuntu nebo Debian.

## 1. Připojení k serveru
V Google Cloud Console klikni na tlačítko **SSH** vedle své instance.

## Důležitá poznámka k IP a DNS

Pokud VM **zastavíš a znovu spustíš** (např. při změně machine type), Google Cloud může přidělit novou **ephemeral external IP**. Pokud není k instanci přiřazená **static external IP**, může se po restartu rozbít `api.polylab.app`, i když kontejnery běží správně.

Po každém `stop/start` nebo změně machine type ověř:

```bash
getent ahosts api.polylab.app | head -n 1
curl -4 ifconfig.me
```

Obě IP adresy musí být stejné. Pokud se liší, aktualizuj DNS `A` record pro `api.polylab.app`.

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
Aplikace by měla běžet na IP adrese tvé instance na portu 80/443 (pokud používáš Caddy). Port 8000 typicky běží jen uvnitř `web` kontejneru a nemusí být publikovaný na hostu.

Otevři v prohlížeči:
- `http://TVOJE_EXTERNAL_IP`
- `https://api.polylab.app` (pokud máš DNS + HTTPS)

Rychlá kontrola po deployi:

```bash
curl -fsS https://api.polylab.app/api/status
```

Pokud `api.polylab.app` neodpovídá, ale kontejnery běží, zkontroluj nejdřív DNS/IP shodu:

```bash
getent ahosts api.polylab.app | head -n 1
curl -4 ifconfig.me
```

## 5. Správa
*   **Logy:** `docker compose logs -f`
*   **Restart:** `docker compose restart`
*   **Stop:** `docker compose down`
