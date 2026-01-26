# Implementation Plan: UI Precision & UX Fixes

Refine UI sliders for better precision, fix the expiry filter functionality, and update mobile filter result reporting to show total counts.

## Phase 1: Backend API Enhancements
Ensure the API provides the total count of filtered results and correctly handles the high-precision price values.

- [ ] Task: Update `GET /api/markets` to return total match count
    - [ ] Modify `get_markets` in `main.py` to return a wrapper object `{ results: [...], total_count: N }` or include a `X-Total-Count` header.
    - [ ] Update SQL query logic to perform a separate `COUNT(*)` or use window functions if performance allows.
- [ ] Task: Verify high-precision price handling in API
    - [ ] Ensure `min_price` and `max_price` query parameters correctly handle 3 decimal places (e.g., `0.999`).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend' (Protocol in workflow.md)

## Phase 2: Frontend Slider Logic & Precision
Implement variable stepping for the probability slider and the logarithmic steps for the expiry slider.

- [ ] Task: Implement Variable Step Probability Slider
    - [ ] In `frontend_deploy/index.html`, update the Vue.js logic for `min_price` and `max_price` sliders.
    - [ ] Add a dynamic `@input` or `:step` handler that switches between `0.1` and `1.0` based on the current value.
- [ ] Task: Implement Logarithmic Expiry Slider
    - [ ] Define the step array: `[1, 6, 24, 168, 720, hours_to_year_end, hours_to_next_year_end]`.
    - [ ] Map the slider index (0-6) to these values when updating `filters.max_hours_to_expire`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Sliders' (Protocol in workflow.md)

## Phase 3: Mobile UX & Total Count Integration
Update the mobile filter interface to show the total results count and fix rendering.

- [ ] Task: Display Total Count in Filter Button
    - [ ] Update the "Show Results" button in the mobile drawer to display the `total_count` from the API.
- [ ] Task: Sync `static/index.html`
    - [ ] Copy `frontend_deploy/index.html` to `static/index.html`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Mobile UX' (Protocol in workflow.md)

## Phase 4: Final Verification & Quality Gates
- [ ] Task: Run full test suite
    - [ ] `python -m unittest discover -s tests -p "*_unittest.py"`
- [ ] Task: Verify byte-parity between frontend files
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final' (Protocol in workflow.md)
