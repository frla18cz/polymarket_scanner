# PolyLab (Polymarket Scanner)

Live: `https://www.polylab.app`
API (backend origin): `https://api.polylab.app`

## Local run

```bash
python --version  # recommended: 3.12+
python -m pip install -r requirements.txt
python scraper.py
./dev_local.sh
```

Open `http://127.0.0.1:8000`.

## Docker (VPS)

```bash
docker compose up --build
```

Notes:

- Logs go to `./logs` (mounted into containers as `/app/logs`).
- `Caddyfile` is configured for `api.polylab.app`; change it if you use a different API host.

## Docs

- `docs/UI_CONTRACT.md`
- `docs/TESTING.md`
- `docs/VERCEL_VPS_GUIDE.md`
- `docs/DEPLOY_INSTRUCTIONS_GCP.md`
- `docs/ROADMAP_IDEAS.md`
- `docs/BUG_REPORT.md`
- `docs/GEMINI.md`
