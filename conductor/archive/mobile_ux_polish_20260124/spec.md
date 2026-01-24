# Track Specification: Mobile UX Polish & Filter Overhaul

## 1. Overview
This track focuses on significantly improving the mobile user experience of PolyLab. The current "filters-first" approach on mobile can feel like a form rather than a product. We will transition to a "results-first" experience where users immediately see market data, with filters accessible via a "Bottom Sheet" style modal. This aims to reduce friction, increase engagement, and modernize the mobile UI.

## 2. User Experience (UX) Goals
- **Results First:** Users land on the market list immediately. If no results are found (e.g., due to restrictive default filters), strictly then might we prompt for action, but the default state should be populated.
- **Bottom Sheet Filters:** Filters are moved to a dedicated, full-screen or bottom-sheet modal on mobile, removing clutter from the main view.
- **Clear Actions:** The filter modal provides clear "Apply", "Reset", and "Close" actions.
- **Context:** Users always know what filters are active via "chips" on the main results view.

## 3. Functional Requirements

### 3.1 Mobile Filter Entry Point
- **Filter Button:** Add a prominent "Filters" button (likely in a sticky sub-header or floating action button) visible on mobile.
- **Onboarding Hint:** (Optional but recommended) On the very first visit, display a subtle, dismissible tooltip or hint pointing to the Filter button: "Tip: Filters are hidden here."

### 3.2 Mobile Filter Modal (Bottom Sheet)
- **Structure:**
    - **Header:** Title ("Filters"), "Close" (X) icon, and "Reset All" button.
    - **Body (Scrollable):**
        - **Primary Section (Always Visible):**
            1.  **Search:** Keyword input.
            2.  **Categories:** Tag inclusion/exclusion inputs.
            3.  **Price/Probability:** Slider range (0-100%).
            4.  **Expiration:** Time sliders/presets.
        - **Advanced Section (Collapsible):**
            - Hidden by default behind a "Show Advanced" toggle.
            - Contains: Spread, Liquidity, Volume, APR, etc.
    - **Footer (Sticky):**
        - **Apply Button:** "Apply Filters (N results)" or just "Show N Results". This gives immediate feedback on how many markets match before closing the modal.

### 3.3 Active Filters Display
- **Filter Chips:** Display a horizontal, scrollable row of "chips" above the market list representing active filters (e.g., "Crypto", "> $5k Vol", "Exp < 24h").
- **Interaction:** Tapping a chip removes/resets that specific filter immediately.

## 4. Technical Implementation
- **Framework:** Vue 3 (CDN) + Tailwind CSS (CDN).
- **Component:** Custom implementation using Tailwind utility classes.
    - Use `fixed inset-0 z-50` for the modal overlay.
    - Use `transform transition-transform` for slide-up animations to mimic a native bottom sheet.
- **State Management:**
    - `showMobileFilters` (Boolean): Controls modal visibility.
    - `showAdvancedFilters` (Boolean): Controls visibility of secondary filters within the modal.
- **Responsiveness:** Changes apply strictly to mobile breakpoints (`md:hidden`). Desktop view remains side-by-side or as currently implemented.

## 5. Success Criteria
- [ ] Mobile users see market results immediately upon load.
- [ ] Filters are accessible via a modal that animates smoothly.
- [ ] "Primary" filters are at the top; "Advanced" filters are collapsible.
- [ ] Active filter chips allow users to clear filters without opening the modal.
- [ ] Mobile Google PageSpeed/Interaction to Next Paint scores are not negatively impacted.
