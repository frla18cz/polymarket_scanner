# Specification: Paid Traffic SEO and Trust Polish (Mar 2026)

## 1. Overview
After the initial paid-traffic readiness wave, PolyLab should tighten crawl hygiene and hero-level trust signaling. The marketing pages should expose structured data for search and social parsers, serve `robots.txt` and `sitemap.xml` consistently in local/backend and Vercel contexts, and surface the core trust points near the hero instead of burying them lower on the page.

## 2. Functional Requirements

### 2.1 Trust Signals
- Homepage and paid landing page must show concise trust/status cues near the hero.
- Trust cues should reinforce: currently free, no wallet required, hourly updates, and independent tool positioning.

### 2.2 Structured Data
- Homepage and landing page must include JSON-LD for `Organization`, `SoftwareApplication`, and `FAQPage`.
- Custom-data page must include JSON-LD for `Organization`, `Service`, and `FAQPage`.

### 2.3 Crawl Files
- Add checked-in `robots.txt` and `sitemap.xml` files for both `frontend_deploy` and `static`.
- `robots.txt` should allow indexable pages, disallow `/app`, and disallow `/landing`.
- `sitemap.xml` should include canonical public pages only: `/` and `/custom-data`.

### 2.4 Serving
- Local/backend frontend mode must serve `/robots.txt` and `/sitemap.xml`.
- Vercel rewrites must explicitly route `/robots.txt` and `/sitemap.xml` to checked-in frontend files.

## 3. Non-Functional Requirements
- Keep mirrored frontend files byte-identical.
- Do not change billing, auth gating, or CTA flow in this track.

## 4. Acceptance Criteria
- [ ] Home and landing heroes expose the new trust/status strip.
- [ ] JSON-LD blocks exist on home, landing, and custom-data pages.
- [ ] `robots.txt` and `sitemap.xml` exist in mirrored frontend/static locations.
- [ ] Local frontend mode and Vercel rewrites resolve the crawl files.
