# Track: UI Stability, Mobile Perf & Deep Linking

## 1. Overview
This track focuses on improving the mobile experience of PolyLab, specifically targeting the "Holders" view and general UI stability. Additionally, it introduces a "Deep Linking" feature to update the URL when a market is opened and adds direct links to Polymarket profiles for holders.

## 2. Functional Requirements

### 2.1 Mobile Verification & Polish
- **Objective:** Ensure core UI components are fully functional and visually coherent on mobile devices.
- **Scope:**
    - **Filter Panel:** Smooth opening/closing, accessible touch targets for sliders and inputs.
    - **Market Details Modal:** Correct layout adaptation, ensure no data is cut off.
    - **Holders View:** Horizontal scrolling or responsive layout to prevent table breakage.

### 2.2 Wallet Address Display & Profile Link (Holders)
- **Behavior:**
    - **Global:** Display wallet addresses in a shortened format (e.g., `0x12...3456`) on ALL devices (Mobile & Desktop).
    - **Polymarket Link:** Instead of just copying, provide a link to the user's profile on Polymarket.
    - **URL Format:** `https://polymarket.com/profile/<wallet_address>`
    - **Desktop Enhancement:** On hover, show the full address in a tooltip (using native `title` attribute).

### 2.3 Deep Linking (Market Details)
- **Mechanism:** Use URL Query Parameters.
- **Behavior:**
    - **On Open:** When a user opens a market details modal, update the URL to append `?market_id=<id>`.
    - **On Close:** When the modal is closed, remove the `market_id` parameter from the URL.
    - **Note:** Initial page load handling of `?market_id` is already implemented and should be preserved.

## 3. Non-Functional Requirements
- **Performance:** Address shortening should not impact rendering performance of large holder lists.
- **Compatibility:** Deep linking must work with the existing hash/routerless setup of the single-file frontend.
- **Parity:** Ensure `frontend_deploy/index.html` and `static/index.html` remain identical.

## 4. Acceptance Criteria
- [ ] Wallet addresses are shortened to `0x...` format in the Holders list on both mobile and desktop.
- [ ] Hovering over a shortened address on desktop reveals the full address.
- [ ] Clicking the profile icon/link opens `https://polymarket.com/profile/<address>` in a new tab.
- [ ] Opening a market updates the URL bar; closing it reverts the URL.
- [ ] Mobile view of Filters and Market Details is verified to be usable and visually broken-free.

## 5. Out of Scope
- Major redesign of the desktop table columns.
- Server-side routing changes (using client-side query params only).