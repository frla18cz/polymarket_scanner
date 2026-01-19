# Implementation Plan: Fix Top Holders Size Magnitude

## Phase 1: Investigation and Reproduction (Red Phase)
- [x] Task: Locate Scaling Logic
    - [x] Identify where `size` is processed in `holders_client.py` or `scraper.py`.
    - [x] Locate the frontend formatting logic for "Top Holders" in `frontend_deploy/index.html`.
- [x] Task: Create Reproduction Test Case
    - [x] Create a new test file `tests/test_holders_scaling_unittest.py`.
    - [x] Write a test that simulates receiving a raw value from the API and checks if the processed/displayed value has the correct magnitude (e.g., 54,000 should not be 54,000,000,000).
    - [x] Confirm the test fails.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (Green Phase)
- [x] Task: Correct Scaling in Backend/Frontend [65b6c4c]
    - [x] Apply the correct decimal division (likely `/ 1e6`) to the raw share count.
    - [x] Update the frontend formatter if necessary to handle the corrected value.
- [x] Task: Verify Fix with Tests [65b6c4c]
    - [x] Run the reproduction tests and ensure they pass.
    - [x] Run existing holders tests to ensure no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Final Verification and Cleanup
- [ ] Task: UI Manual Verification
    - [ ] Run the application locally and verify that a market's Top Holders now show "k" or "M" appropriately instead of "b" or "T".
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Verification and Cleanup' (Protocol in workflow.md)
