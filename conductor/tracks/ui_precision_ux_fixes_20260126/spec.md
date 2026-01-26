# Specification: UI Precision & UX Fixes (Jan 2026)

## 1. Overview
This track focuses on refining the user experience of the PolyLab scanner by fixing broken UI components and improving precision for professional traders. Key areas include the Probability/Price slider, the Expiry slider, and the mobile filter result reporting.

## 2. Functional Requirements

### 2.1 Variable Precision Probability Slider
- **Behavior:** The Probability/Price slider (min_price/max_price) must support variable step increments.
- **Precision Rules:**
  - **Edges (0% - 1% and 99% - 100%):** Step increment of **0.1%** (e.g., 99.8% -> 99.9%).
  - **Middle (1% - 99%):** Step increment of **1%**.
- **UI Feedback:** Ensure the numeric labels correctly reflect the high-precision values (e.g., "99.9%").

### 2.2 Logarithmic "Expires Within" Slider
- **Behavior:** Replace the current (broken) linear slider with a logarithmic/stepped slider.
- **Fixed Steps:**
  - 1 hour
  - 6 hours
  - 24 hours
  - 7 days
  - 30 days
  - End of Current Year
  - End of Next Year
- **Requirement:** Ensure the slider correctly communicates these values to the `max_hours_to_expire` API parameter.

### 2.3 Total Match Count in Mobile Filters
- **Behavior:** On mobile, the "Show Results" button (or equivalent count indicator in the filter drawer) must display the **total number of markets** matching the filters in the entire database.
- **Implementation Note:** Even if the UI only renders the first 100 items for performance, the count shown to the user during filtering must be accurate (e.g., "Show 452 Results").
- **Constraint:** We continue to load/render only 100 items in the list view per the user's preference for now.

## 3. Non-Functional Requirements
- **Performance:** Calculating the total count must not significantly degrade API response time.
- **Consistency:** Ensure `frontend_deploy/index.html` and `static/index.html` remain byte-identical.

## 4. Acceptance Criteria
- [ ] Probability slider allows selecting "99.9%" and "0.1%".
- [ ] "Expires Within" slider moves between the defined steps (1h, 6h, etc.) and filters markets correctly.
- [ ] Mobile filter button displays "Show [Total] Results" where Total is the full count of matches, not capped at 100.
- [ ] All unit tests (including `test_frontend_contract_unittest.py`) pass.

## 5. Out of Scope
- Implementing "Load More" or Infinite Scroll (deferred to a future track).
- Changes to the backend database schema.
