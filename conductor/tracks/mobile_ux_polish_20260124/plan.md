# Implementation Plan: Mobile UX Polish & Filter Overhaul

This plan details the transition from a "filters-first" mobile UI to a "results-first" experience with a bottom-sheet modal and active filter chips, following the project's TDD and UX-first workflow.

## Phase 1: Foundation & "Results-First" Logic
Goal: Ensure the app loads results immediately on mobile and prepare the state for modal control.

- [x] Task: Update `index.html` state to default `showMobileFilters` to `false`.
- [x] Task: Ensure the market fetching logic handles the initial load correctly without requiring user interaction on mobile.
- [x] Task: Write a test in `tests/test_ui_mobile_polish_contract_unittest.py` to verify that markets are visible on a simulated mobile viewport without opening filters.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Results-First' (Protocol in workflow.md)

## Phase 2: Mobile Filter Modal (Bottom Sheet)
Goal: Implement the custom Tailwind bottom-sheet component.

- [ ] Task: Create the `MobileFilterModal` template structure inside `index.html`.
- [ ] Task: Implement the slide-up animation using Tailwind transition classes and Vue `v-if`/`v-show`.
- [ ] Task: Implement the "Primary" vs "Advanced" section logic within the modal.
- [ ] Task: Implement the sticky footer with the "Show N Results" button.
- [ ] Task: Write tests to verify the modal opens/closes and toggles the advanced section correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Bottom Sheet' (Protocol in workflow.md)

## Phase 3: Active Filter Chips
Goal: Provide immediate feedback and quick removal of filters.

- [ ] Task: Implement the `activeFilterChips` computed property to generate labels for current filters.
- [ ] Task: Create the horizontal scrollable chips UI above the market list.
- [ ] Task: Bind click events on chips to reset specific filter values in the Vue state.
- [ ] Task: Write tests to verify that removing a chip correctly resets the corresponding filter and triggers a re-fetch.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Active Chips' (Protocol in workflow.md)

## Phase 4: UX Polish & Cleanup
Goal: Final touches on transitions, hints, and mobile-specific styling.

- [ ] Task: Implement the "First Visit Hint" (tooltip) pointing to the filter button using `localStorage` to track if seen.
- [ ] Task: Refine the "Show N Results" feedback logic to update as user changes filters inside the modal.
- [ ] Task: Final CSS cleanup for touch targets (ensure buttons are at least 44x44px per guidelines).
- [ ] Task: Verify overall mobile performance and accessibility.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Polish' (Protocol in workflow.md)
