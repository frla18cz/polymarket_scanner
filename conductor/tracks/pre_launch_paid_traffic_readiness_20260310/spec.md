# Specification: Pre-Launch Paid Traffic Readiness (Mar 2026)

## 1. Overview
PolyLab is about to send colder traffic from X and paid campaigns into the marketing homepage, paid landing page, and public app. Before launch, the web experience should remove misleading paid-tier language, preserve attribution after the first click into `/app`, expose better activation signals, prevent the paid landing from competing in search indexing, and reduce avoidable mobile landing cost.

## 2. Functional Requirements

### 2.1 Messaging Consistency
- Marketing pages and the public app must consistently present PolyLab as currently free during early access.
- The public app must not label the auth/login surface as a paid `Pro` tier.
- Existing auth-gated preset behavior may remain, but the wording must describe account access rather than payment.

### 2.2 Attribution Continuity
- Shared tracking must preserve first-touch campaign context across internal navigation to `/app`.
- Later events without live UTM params must still carry the original campaign attribution.
- No new database migration is required in this iteration.

### 2.3 Activation Tracking
- The app must emit a minimal set of post-click activation events beyond `page_view` and generic CTA clicks.
- Activation should cover first market load, first filter interaction, outbound market open, Smart Money entry, and password login start/failure.

### 2.4 Indexing Control
- `/` and `/custom-data` remain indexable with canonical tags.
- `/landing` and `/app` must include `noindex,follow` and canonical tags.

### 2.5 Performance Hygiene
- Below-the-fold marketing proof images must be lazy-loaded.
- The landing hero media must behave more conservatively on small screens and reduced-motion environments.

## 3. Non-Functional Requirements
- `frontend_deploy` and `static` copies must remain mirrored.
- Keep the existing route structure unchanged.
- Do not add billing, a lead form, or new backend APIs in this track.

## 4. Acceptance Criteria
- [ ] App auth copy no longer implies a paid Pro tier.
- [ ] Attribution survives the landing-to-app transition without requiring UTM params on `/app`.
- [ ] New activation events are present in the app contract.
- [ ] `/landing` and `/app` are marked `noindex,follow`.
- [ ] Marketing proof media uses lazy-loading for non-active images.
- [ ] Mirrored frontend files remain byte-identical.
