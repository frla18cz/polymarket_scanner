# Specification: Homepage Smart Money Signal Deep Link Fix

## 1. Overview
Fix the homepage Smart Money signal handoff so the "Open in scanner" CTA opens the exact market the visitor was inspecting, instead of dropping them into a generic or unrelated app state.

## 2. Functional Requirements

### 2.1 Smart Money Signal CTA
- The homepage Smart Money signal modal CTA must deep-link into `/app` with the currently expanded market.
- The link must include the specific `market_id`.
- The link must include `view=smart` so the scanner opens in the Smart Money view.

### 2.2 Scanner Compatibility
- The generated URL must use the existing scanner query contract and remain compatible with the current `market_id` deep-link behavior.

## 3. Non-Functional Requirements
- Keep `static/index.html` and `frontend_deploy/index.html` behavior in sync.
- Preserve current homepage analytics attributes on the CTA.

## 4. Acceptance Criteria
- [ ] Clicking "Open in scanner" from a homepage Smart Money signal opens `/app` with `market_id=<selected market>` and `view=smart`.
- [ ] The existing app deep-link logic can expand the targeted market without additional user input.
- [ ] Targeted homepage/app contract tests pass.
