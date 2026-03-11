# Specification: Landing Early-Access Copy Cleanup (Mar 2026)

## 1. Overview
PolyLab currently presents homepage and landing-page messaging that implies a live Free vs Pro split, even though there is no active paid subscription or checkout. The marketing copy should instead describe the product as currently free during early access, while leaving room for future monetization without promising unavailable plans.

## 2. Functional Requirements

### 2.1 Marketing Message
- Homepage and paid landing page must describe PolyLab as currently free during early access.
- Copy must state or clearly imply that no paid subscription exists yet.
- Copy may mention that paid plans could be introduced later, but must not present a live upgrade path.

### 2.2 Pricing / Access Section
- Remove the explicit "Free vs Pro" framing from homepage and landing navigation/section copy.
- Replace the pricing section content with accurate early-access messaging.
- Do not introduce prices, billing UI, or checkout language.

### 2.3 Shared Info Content
- Update shared FAQ copy so it no longer references current Pro-only capabilities.
- Keep the FAQ aligned across homepage, landing page, and any shared info surfaces.

## 3. Non-Functional Requirements
- Keep `frontend_deploy` and `static` marketing files mirrored.
- Preserve the existing page structure and CTA routing.
- Keep the tone direct and factual, consistent with PolyLab product guidelines.

## 4. Acceptance Criteria
- [ ] Homepage no longer presents a live Free vs Pro comparison.
- [ ] Landing page no longer presents a live Free vs Pro comparison.
- [ ] Shared FAQ copy states that PolyLab is currently free during early access.
- [ ] `static` and `frontend_deploy` copies remain byte-identical for mirrored files.

## 5. Out of Scope
- Launching billing or checkout.
- Announcing pricing numbers or launch dates for paid plans.
- Adding gated premium features to the app.
