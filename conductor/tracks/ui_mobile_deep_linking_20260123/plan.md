# Implementation Plan - UI Stability, Mobile Perf & Deep Linking

## Phase 1: Deep Linking & URL Updates
- [x] Task: Create/Update test file `tests/test_ui_deep_linking_contract_unittest.py` [adb21bb]
    - [ ] Create test class `TestDeepLinkingContract`
    - [ ] Add test `test_url_update_logic_exists` (Expects `window.history.pushState` or `replaceState` calls when selecting/deselecting market)
- [x] Task: Implement URL Synchronization in `frontend_deploy/index.html` [adb21bb]
    - [ ] Add `watch` or method to update URL when `selectedMarket` changes.
    - [ ] Ensure URL is cleaned up when modal is closed.
    - [ ] Ensure `frontend_deploy/index.html` is copied to `static/index.html`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Deep Linking & URL Updates' (Protocol in workflow.md)

[checkpoint: f86fa8c]

## Phase 2: Mobile Polish & Holders Profile Links
- [x] Task: Create new test file `tests/test_ui_mobile_polish_contract_unittest.py` [f9bf3d1]
    - [x] Create test class `TestMobilePolishContract` [f9bf3d1]
    - [x] Add test `test_address_shortening_logic_exists` (Expects function `shortenAddress`) [f9bf3d1]
    - [x] Add test `test_profile_link_exists` (Expects link to `polymarket.com/profile/`) [f9bf3d1]
    - [x] Add test `test_tooltip_attribute_exists` (Expects `title="..."` binding on address) [f9bf3d1]
- [x] Task: Implement Address Shortening & Profile Links [f9bf3d1]
    - [x] Create `shortenAddress` function in `frontend_deploy/index.html`. [f9bf3d1]
    - [x] Update Holders table/list to use it. [f9bf3d1]
    - [x] Add link to Polymarket profile with an external link icon. [f9bf3d1]
    - [x] Add `title` attribute for desktop tooltip. [f9bf3d1]
    - [x] Ensure `frontend_deploy/index.html` is copied to `static/index.html`. [f9bf3d1]
- [ ] Task: Verify and Fix Mobile Layouts
    - [ ] Check Filter Panel (CSS adjustments if needed).
    - [ ] Check Market Details Modal (CSS adjustments).
    - [ ] Check Holders View (CSS adjustments for scrolling/wrapping).
    - [ ] Ensure `frontend_deploy/index.html` is copied to `static/index.html`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mobile Polish & Holders Profile Links' (Protocol in workflow.md)

## Phase 3: Final Integration & Cleanup
- [ ] Task: Run Full Test Suite
    - [ ] Run `python -m unittest discover tests` to ensure no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Integration & Cleanup' (Protocol in workflow.md)