# Track: Production Auth & API Fix (2025-12-27)

## Status: Completed ✅

## Problem Statement
1.  **Auth Redirects:** Users were being redirected to `localhost` after login on the production site.
2.  **Data Loading:** The production frontend (`polylab.app`) was unable to fetch data from the API due to a "502 Bad Gateway" error.

## Actions Taken
1.  **Supabase Configuration:** 
    *   Added `https://www.polylab.app` and `https://polylab.app` to the allowed Redirect URLs in Supabase Dashboard.
    *   Updated `docs/AUTH_SETUP.md` to reflect these requirements.
2.  **Infrastructure (DNS):**
    *   Created/Verified DNS A record for `api.polylab.app` pointing to the VPS IP (`35.238.7.116`).
3.  **Backend (HTTPS/Caddy):**
    *   Restarted Caddy on the VPS to trigger ACME certificate issuance for the new `api.polylab.app` domain.
    *   Verified successful certificate acquisition in Caddy logs.
4.  **Verification:**
    *   Confirmed `https://api.polylab.app/api/status` returns valid JSON with valid SSL.
    *   Confirmed `https://www.polylab.app` correctly fetches and displays market data.

## Key Learnings
*   When moving from IP-based API destination to domain-based destination in `vercel.json`, DNS must be updated BEFORE deployment to avoid Caddy failing to obtain SSL certificates.
*   Always ensure all production domain variants are whitelisted in Supabase Auth.
