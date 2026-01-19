# Specification: Fix Top Holders Size Magnitude

## 1. Overview
The 'size' metric displayed in the "Top Holders" view (accessible after clicking a specific event) shows values that are incorrectly scaled by a massive order of magnitude. For example, a value that should be **54k** (shares) is currently displayed as **54b**.

This track aims to investigate the data pipeline (API response -> Frontend display) to identify the scaling error and correct the displayed values to reflect reality.

## 2. Problem Description
*   **Location:** Frontend -> Event Detail -> Top Holders list.
*   **Metric:** 'Size' (representing position size/shares).
*   **Symptom:** Values are off by a factor of 1,000,000 (10^6) or similar, showing "Billions" instead of "Thousands".
*   **Example:** User reports seeing "54b" where the actual value on Polymarket is "54k".

## 3. Root Cause Hypothesis
*   **Likely Cause:** The raw data from the backend (or Goldsky/Polymarket API) might be in a smaller unit (e.g., raw units, wei) and is not being divided by the appropriate decimal factor (likely 6 for USDC/shares) before being formatted for display.
*   **Alternative:** The frontend formatter might be misinterpreting the input number.

## 4. Functional Requirements
*   **Correct Scaling:** The 'size' value in the Top Holders table must be divided/scaled correctly so that "54,000" shares appears as "54k" (or "54,000"), not "54b".
*   **Consistency:** Verify if this scaling issue affects other similar metrics in the same view (e.g., 'Value' if present).

## 5. Acceptance Criteria
*   [ ] The 'size' column in the Top Holders view displays values matching the actual share count (e.g., 54k shares).
*   [ ] The fix works for both large and small holders.
*   [ ] No other metrics in the view are negatively impacted.
