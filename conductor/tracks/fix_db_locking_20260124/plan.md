# Plan: Fix Database Locking via Sequential Chaining

This plan refactors `auto_refresh.py` to eliminate race conditions between the main market scraper and the smart money scraper by ensuring they run sequentially.

## Phase 1: Preparation and Test Setup
- [x] Task: Create a regression test for `auto_refresh.py` logic 8f268a9
    - [x] Create `tests/test_auto_refresh_logic_unittest.py`
    - [x] Mock `run_scrape` and `run_smart_money` to verify they are called in order
    - [x] Verify that an exception in `run_scrape` prevents `run_smart_money` from executing
- [x] Task: Conductor - User Manual Verification 'Phase 1: Preparation and Test Setup' (Protocol in workflow.md) [checkpoint: 8f268a9]

## Phase 2: Implementation of Chained Execution
- [x] Task: Refactor `auto_refresh.py` to support chaining 8f268a9
    - [x] Implement a unified `job_coordinated_refresh(force_smart_money=False)` function
    - [x] Update `job_scrape` to use this unified logic
    - [x] Update `job_smart_money` to use this unified logic
    - [x] Ensure `log_stats` captures both durations accurately
- [x] Task: Update APScheduler configuration 8f268a9
    - [x] Modify `start_scheduler` to avoid simultaneous `next_run_time` for the initial run
    - [x] (Alternative) Consolidate into a single job if acceptable, or keep separate but remove immediate start for Smart Money
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation of Chained Execution' (Protocol in workflow.md)

## Phase 3: Final Verification & Cleanup
- [x] Task: Verify stats logging integrity a55ab6a
    - [x] Run a manual cycle and check `logs/scrape_stats.csv`
- [x] Task: Final code review and linting a55ab6a
    - [x] Ensure no side effects or deadlocks remain
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Verification & Cleanup' (Protocol in workflow.md) [checkpoint: a55ab6a]