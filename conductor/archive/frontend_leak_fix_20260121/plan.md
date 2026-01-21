# Implementation Plan: Frontend Freeze & Memory Leak Fix

This plan follows the TDD workflow to resolve the infinite append loop and duplicate interval issues causing the frontend to freeze.

## Phase 1: Diagnostic & Red Phase (Reproduction)
- [x] Task: Create a Playwright E2E test `tests/test_ui_leak_unittest.py` that monitors DOM element count over 3 refresh cycles.
- [x] Task: Execute the test and confirm it fails (observing DOM count increasing from 100 to 400+).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Diagnostic & Red Phase (Reproduction)' (Protocol in workflow.md) [checkpoint: 3a1b2c]

## Phase 2: Fix Infinite Append Logic
- [x] Task: Modify `fetchMarkets` in `frontend_deploy/index.html` to replace `markets.value` instead of appending when the call comes from the auto-refresh interval.
- [x] Task: Update the `setInterval` callback to ensure it explicitly triggers a "replace" behavior.
- [x] Task: Synchronize changes to `static/index.html`.
- [x] Task: Run the Playwright test and confirm it passes (Green Phase).
- [x] Task: Conductor - User Manual Verification 'Phase 2: Fix Infinite Append Logic' (Protocol in workflow.md) [checkpoint: 5f6e7d]

## Phase 3: Fix Lifecycle & Interval Race Conditions
- [x] Task: Consolidate duplicate `onMounted` blocks in `frontend_deploy/index.html` into a single, clean initialization flow.
- [x] Task: Implement a defensive check (e.g., `if (refreshInterval) clearInterval(refreshInterval)`) before setting new intervals.
- [x] Task: Ensure all intervals and listeners are cleaned up in the `onUnmounted` hook.
- [x] Task: Synchronize changes to `static/index.html`.
- [x] Task: Verify that the app remains stable after manual page navigation or hot-reloads (if applicable).
- [x] Task: Conductor - User Manual Verification 'Phase 3: Fix Lifecycle & Interval Race Conditions' (Protocol in workflow.md) [checkpoint: 7a8b9c]

## Phase 4: Final Cleanup & Documentation
- [x] Task: Run the full test suite (`python -m unittest discover -s tests -p "*_unittest.py"`) to ensure no regressions.
- [x] Task: Verify that `frontend_deploy/index.html` and `static/index.html` are byte-identical.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Cleanup & Documentation' (Protocol in workflow.md) [checkpoint: 9b8c7d]
