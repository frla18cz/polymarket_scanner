## Loading Overlay Issue

**Description:** The loading overlay implemented in `static/index.html` to indicate data fetching upon filter changes or preset application does not appear to be functioning ideally, or at all, for the user. The user observes that "nothing happens, only old data changes to new data."

**Expected Behavior:**
- When a filter is changed or a preset is applied (triggering `resetAndFetch` which calls `fetchMarkets(false)`), the loading overlay should immediately appear, visually indicating that new data is being fetched.
- The overlay should remain visible until the `fetchMarkets` operation completes successfully or fails.

**Observed Behavior:**
- The loading overlay is not consistently visible, or visible at all, when filters or presets are changed.
- The transition from old data to new data appears instantaneous, without the expected loading indicator.

**Potential Causes to Investigate:**
- **`loading` variable state:** Ensure `loading.value` is correctly set to `true` at the beginning of `fetchMarkets` (when `append` is false) and `false` after the fetch completes.
- **Vue reactivity:** Confirm that Vue is reacting to changes in `loading.value` and updating the DOM accordingly.
- **CSS `z-index` and positioning:** Double-check that the overlay's CSS (`absolute inset-0 z-[100]`) is effectively placing it above all other content and that no other elements are inadvertently covering it.
- **JavaScript execution speed:** If the API response is extremely fast on localhost, the loading state might toggle too quickly to be visually perceptible. (Less likely given user's report of "5 seconds" delay).
- **`v-show` vs `v-if` interaction:** While `v-show` keeps the element in the DOM, there might be a subtle timing issue with its display property.

**Next Steps:**
- Re-verify the `loading` variable's lifecycle in the `fetchMarkets` function and its impact on the `v-show` directive.
- Consider adding temporary console logs to track the `loading.value` state during filter changes.
- Explore adding a small artificial delay (e.g., `setTimeout`) to `loading.value = false` in development to ensure the overlay is visible for testing purposes.

