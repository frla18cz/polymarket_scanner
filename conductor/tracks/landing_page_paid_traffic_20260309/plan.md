# Implementation Plan: Paid-Traffic Landing Page

Create a dedicated landing page for paid traffic while keeping the existing scanner homepage unchanged.

## Phase 1: Route and Contract Setup
- [x] Task: Add failing tests for landing page contract, SEO metadata, and frontend route behavior.
- [x] Task: Add dedicated `/landing` route while preserving `/` as the scanner route.

## Phase 2: Landing Page Build
- [x] Task: Create lightweight landing page HTML for `frontend_deploy`.
- [x] Task: Mirror the landing page to `static` and keep files byte-identical.
- [x] Task: Reuse existing demo assets and current product claims only.

## Phase 3: Messaging, Proof, and Verification
- [x] Task: Implement approved landing page structure and CTA flow for general Polymarket traders.
- [x] Task: Add dedicated landing page SEO/Open Graph/Twitter metadata.
- [x] Task: Run targeted tests for the new landing page and full frontend contract coverage.

## Phase 4: Product Proof Polish
- [x] Task: Replace the single proof screenshot with a tabbed multi-view product gallery.
- [x] Task: Generate dedicated proof images for Scanner, Smart Money, and Yield + Filters states.
- [x] Task: Re-run landing asset and contract tests after the proof gallery upgrade.

## Phase 5: Homepage and Shared Info Unification
- [x] Task: Promote `/` to a marketing homepage and move the scanner frontend to `/app`.
- [x] Task: Preserve root deep-link compatibility by redirecting `/?market_id=...` to `/app?...`.
- [x] Task: Extract shared FAQ, Terms, Privacy, and Contact content into shared frontend assets used by app, homepage, and landing.
- [x] Task: Re-run homepage, landing, app, route, and shared-asset contract tests after the route split.

## Phase 6: Custom Data Funnel
- [x] Task: Add a new `/custom-data` marketing page for funds, research desks, and builders.
- [x] Task: Add a homepage teaser section and a lower-page landing callout that point to `/custom-data`.
- [x] Task: Extend shared marketing copy assets for custom-data teaser, callout, page CTA, and B2B FAQ.
- [x] Task: Update local frontend routes and Vercel rewrites so `/`, `/landing`, `/app`, and `/custom-data` resolve to dedicated HTML entry points.
- [x] Task: Re-run targeted route, contract, shared-copy, and Vercel routing tests after the B2B funnel additions.
