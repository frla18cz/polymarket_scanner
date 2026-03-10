# Specification: Paid-Traffic Landing Page (Mar 2026)

## 1. Overview
PolyLab needs a dedicated landing page for cold paid traffic instead of sending ad clicks straight into the existing app-first scanner. The landing page should explain the product in under five seconds, show product proof using real UI, and route interested users into the existing public scanner without forcing signup first.

## 2. Functional Requirements

### 2.1 Route Strategy
- Add a dedicated public landing page at `/landing` and `/landing/`.
- Keep the current root route `/` as the app-first scanner experience.
- Do not change backend API contracts.

### 2.2 Messaging and Audience
- The landing page must be in English.
- Primary audience: general Polymarket traders.
- Positioning should emphasize faster market discovery and cleaner trade evaluation over generic "analytics platform" language.

### 2.3 Landing Page Structure
- Hero with a strong outcome-focused headline, one supporting sentence, product media, and two CTAs.
- Value proposition section translating scanner capability into trader outcomes.
- Product proof section using real PolyLab UI and concrete proof points already supported by the product.
- "How it works" section with a simple three-step workflow.
- Free vs Pro section without hard-coded pricing numbers.
- FAQ and final CTA.

### 2.4 CTA Behavior
- Primary CTA should send users directly to `/`.
- Secondary CTA should stay on the landing page and jump to the product demo/proof section.
- Above the fold must not show login forms or premium gating.

## 3. Non-Functional Requirements
- The landing page should be lightweight and not boot the full scanner app bundle.
- Reuse existing product assets where possible (`demo.gif`, `demo.webm`, `demo.mp4`, brand logo).
- Keep `frontend_deploy` and `static` copies byte-identical for the landing page, same as the main app HTML.
- The page must work on desktop and mobile and preserve the existing dark PolyLab visual language.

## 4. Acceptance Criteria
- [ ] `/landing` loads a dedicated marketing page while `/` still loads the scanner.
- [ ] The landing page contains the approved hero, proof, FAQ, and CTA structure.
- [ ] Primary CTA opens the scanner without an auth wall.
- [ ] Landing page has dedicated SEO/Open Graph/Twitter meta tags.
- [ ] `static/landing/index.html` and `frontend_deploy/landing/index.html` are identical.

## 5. Out of Scope
- Moving the marketing landing to `/`.
- Introducing new pricing numbers or billing logic.
- Adding testimonials or external social proof assets.
