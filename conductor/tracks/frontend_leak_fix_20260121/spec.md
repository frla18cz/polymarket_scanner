# Specification: Frontend Freeze & Memory Leak Fix

## 1. Overview
This track addresses a critical performance issue on the PolyLab frontend where the application freezes after running for a period of time. The root causes have been identified as a logic error in the auto-refresh mechanism causing infinite data appending, and a potential race condition with duplicate interval timers.

## 2. Problem Description
The application exhibits a memory leak and progressive UI lag leading to a freeze. Two primary issues were identified:
1.  **Infinite Append Loop:** The `fetchMarkets(true)` function is called every 30 seconds by an auto-refresh interval. It unconditionally appends new fetched markets to the existing `markets` array. This causes the dataset and the resulting DOM elements to grow indefinitely (e.g., +100 items every 30s).
2.  **Duplicate Intervals:** The `onMounted` lifecycle hook may be initializing multiple `setInterval` timers without properly clearing previous ones, leading to "zombie" timers that cannot be cancelled and compound the resource usage.

## 3. Functional Requirements
*   **Fix Auto-Refresh Logic:** The `fetchMarkets` function (or the interval callback) must be updated to **update** or **replace** existing market data during an auto-refresh, rather than appending duplicates to the list. Appending should only occur during explicit "Load More" user actions.
*   **Fix Interval Management:** Ensure that the `refreshInterval` is properly cleared before being set. Add safeguards to prevent multiple intervals from running simultaneously (e.g., check if an interval ID already exists).
*   **Resource Cleanup:** Ensure `clearInterval` and `removeEventListener` are called correctly in `onUnmounted` or `beforeUnmount`.

## 4. Verification & Testing
*   **Automated E2E Test (Playwright):**
    *   Create a new test file `tests/test_ui_leak_unittest.py`.
    *   The test should load the page, wait for the initial load, and then accelerate time or wait for multiple auto-refresh cycles.
    *   **Success Criteria:** The number of market cards (DOM elements) must remain stable (equal to the page limit, e.g., 100) and not increase after auto-refresh cycles.

## 5. Affected Files
*   `frontend_deploy/index.html` (Production frontend)
*   `static/index.html` (Local dev frontend - must be kept in sync)
