# Implementation Plan: Homepage Smart Money Signal Deep Link Fix

Fix the homepage Smart Money signal CTA so it hands the user off into the exact market inside the Smart Money scanner view.

## Phase 1: Contract and Implementation
- [x] Task: Add a failing homepage contract test for Smart Money signal deep-link parameters. [657706c]
- [x] Task: Implement a homepage Smart Money CTA URL builder that includes `market_id` and `view=smart`. [657706c]
- [x] Task: Sync `static/index.html` and `frontend_deploy/index.html`. [657706c]
- [x] Task: Run the targeted deep-linking/homepage test suite. [657706c]
