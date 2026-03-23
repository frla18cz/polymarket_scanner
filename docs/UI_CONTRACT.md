# UI Contract (Desktop + Mobile)

This document captures the **expected/required UI + API behavior** so we can keep the “production desktop” feature set **always present** and **identical on mobile** (same filters + same details, only different layout).

## Frontend files

The app UI is a single static HTML file (Vue + Tailwind):

- `frontend_deploy/app/index.html` (served by FastAPI when `SERVE_FRONTEND=1`)
- `static/app/index.html` (kept **byte-identical** to `frontend_deploy/app/index.html` for alternate hosting)

Rule: **edit `frontend_deploy/app/index.html` and copy it to `static/app/index.html`** (there is a unit test that enforces this).

## API surface (required)

- `GET /api/homepage-bootstrap` → snapshot-backed homepage payload (spotlight cards, playbook previews, freshness timestamps)
- `GET /api/app-bootstrap?view=scanner|smart&preset=<id>` → snapshot-backed first-paint payload for `/app`, smart view, and preset deep-links
- `GET /api/tags` → list of tags for include/exclude autocomplete
- `GET /api/status` → `{ last_updated }` timestamp shown in header
- `GET /api/markets` → live scanner data for interactive filtering, pagination, and silent refresh (supports all filters below)
- `GET /api/markets/{market_id}/holders` → list of top holders with P/L stats for a specific market
  - Response Model: `List[HolderDetail]`
  - Fields: `wallet_address`, `position_size`, `outcome_index`, `total_pnl`, `alias` (optional)

Bootstrap-first rule:

- Homepage first paint should come from `/api/homepage-bootstrap`, optionally hydrated from `localStorage`.
- App first paint should come from `/api/app-bootstrap`, optionally hydrated from `sessionStorage` / `localStorage`.
- The frontend may revalidate with live `/api/markets` after first paint, but should not require a second blocking fetch before rendering the initial list.

## Required filters (UI → `/api/markets` query params)

All filters must work the same on desktop and mobile because they share the same state.

- **Included categories**
  - UI: `filters.includedTags: string[]`
  - API: `included_tags=tagA,tagB,...` (comma-separated)
  - Semantics: **ANY-match** (at least one selected tag).
- **Excluded categories**
  - UI: `filters.excludedTags: string[]`
  - API: `excluded_tags=tagA,tagB,...` (comma-separated)
  - Semantics: market is excluded if it has **any** excluded tag.
- **Expires within**
  - UI: `filters.max_hours_to_expire: number` (0 = anytime)
  - API: `max_hours_to_expire=<int hours>` (omit when 0)
- **Not sooner than (min time to expire)**
  - UI: `filters.min_hours_to_expire: number` (0 = any)
  - API: `min_hours_to_expire=<int hours>` (omit when 0)
  - Semantics: `end_date >= now + min_hours_to_expire`
- **Include expired**
  - UI: `filters.include_expired: boolean`
  - API: `include_expired=true|false`
- **Price / probability range**
  - UI: `filters.min_price`, `filters.max_price` in `[0..1]`
  - API: `min_price`, `max_price`
- **Max spread**
  - UI: `filters.max_spread` (fraction, e.g. `0.05` = 5¢)
  - API: `max_spread`
- **Min APR (Win)**
  - UI: `filters.min_apr_percent` (percent, e.g. `150` = 150%)
  - API: `min_apr` (fraction, e.g. `1.5` = 150%) (omit when 0)
- **Min volume / liquidity**
  - UI: `filters.min_volume`, `filters.min_liquidity`
  - API: `min_volume`, `min_liquidity`
- **Smart Money Analysis (Dominance)**
  - UI: `filters.min_profitable`, `filters.min_losing_opposite`
  - API:
    - `min_profitable` (int): Min number of profitable holders on THIS outcome.
    - `min_losing_opposite` (int): Min number of losing holders on the OPPOSITE outcome.
  - Semantics: Holders are counted by PnL sign (`total_pnl > 0` profitable, `total_pnl < 0` losing).
- **Search**
  - UI: `filters.search`
  - API: `search=<string>` (omit when empty)
- **Sort**
  - UI: `filters.sort_by`, `filters.sort_dir`
  - API:
    - `sort_by` in `volume_usd|liquidity_usd|end_date|price|spread|apr|question|yes_profitable_count|yes_losing_count|yes_total|no_profitable_count|no_losing_count|no_total`
    - `sort_dir` in `asc|desc`
- **Pagination**
  - UI: fixed `limit=100`, `offset` increments by 100
  - API: `limit`, `offset`

Notes:

- The frontend always includes a cache-buster `_t=<timestamp>`; the backend returns `Cache-Control: no-cache`.
- Tag params are sent as comma-separated strings for proxy safety; the backend splits them into lists.
- `smart_money_win_rate` is not part of the current public app contract even though the background job still stores it internally.

## Required market fields (shown in UI details)

Both desktop and mobile “details” must include (when available):

- Link to market (`url`)
- Copy Market ID (`market_id`) and Copy Link
- Condition ID (`condition_id`) for holders lookup
- Event slug (`event_slug`) if present
- Probability (`price`), spread (`spread`), APR (`apr`), volume (`volume_usd`), liquidity (`liquidity_usd`)
- Dates (`start_date`, `end_date`) and relative expiry (“in X days” / “Expired”)
- Category (`category`) and outcome (`outcome_name`)
- Derived: implied odds (`1 / price`)

## Deep-link contract

- `market_id=<market_id>` expands the matching market row after load.
- `preset=<preset_id>` resolves a known preset and should be consumed before the first app data request.
- `view=scanner|smart` selects the app view after load.
- `Smart Money Edge` homepage CTA should deep-link as `preset=smart_money_edge&view=smart`.

## Deployment expectations

- **Same-origin deploy (recommended):** serve UI and `/api` from the same host (FastAPI serves HTML, or reverse-proxy). `API_BASE_URL` should stay empty (`""`).
- **Split deploy:** if the frontend is hosted separately, use a rewrite/proxy so the frontend can still call `/api/*` on its own origin. If you cannot do that, set `API_BASE_URL` to the API origin and configure CORS + HTTPS accordingly.

## Required UI structure (desktop + mobile)

The UI is one file and must keep feature parity:

- Desktop uses the full table layout.
- Mobile uses cards + a filter overlay, but **the same filters and the same details** must be available.

### Sidebar (filters)

The sidebar must include:

- **Presets** (at least: Safe Haven, YOLO, Warren Buffett, Sniper/Last Min) and a “Show More/Show Less” toggle when more presets exist.
- **Search Markets**
- **Include Categories** (with an `ALL` reset action)
- **Exclude Categories** (with a `Clear` action)
- **Expires Within** slider + quick buttons: `24h`, `7d`, `30d`, `End this year`, `End next year`, `Anytime`
- **Not Sooner Than** quick buttons: `Any`, `24h`, `48h`, `7d`
- **Include Past Due (Expired)** toggle
- **Outcome Price Range (Probability)** (min + max sliders)
- **Max Spread**
- **Min APR (Win)**
- **Min Volume**
- **Min Liquidity**
- **Compact Rows** toggle (desktop table density)

### Desktop table

The table must provide at least these columns (and sorting where applicable):

- Icon
- Market (sort by `question`)
- Price (sort by `price`)
- Spread (sort by `spread`)
- APR (sort by `apr`)
- Volume (sort by `volume_usd`)
- Liq (sort by `liquidity_usd`)
- Expires (sort by `end_date`)

### Mobile UX

- Default is **Cards** on narrow screens, with a quick toggle to **Table** (so users can choose).
- The filters drawer may auto-open once on first visit to make discoverability obvious.
