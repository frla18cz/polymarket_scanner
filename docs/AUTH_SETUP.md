# Supabase Auth Setup

## Overview
PolyLab uses Supabase for authentication. Currently, it supports **Google OAuth** and **Email/Password** (via Magic Link or Password).

- **Frontend:** Implemented in `frontend_deploy/app/index.html` (and synced to `static/app/index.html`).
- **SDK:** Uses `@supabase/supabase-js` v2 via CDN.
- **State:** Auth state is managed reactively in Vue `user` ref.

## Configuration

### Environment Variables
The following keys are stored in `.env` (and injected/hardcoded in frontend HTML for the Anon key):

- `SUPABASE_URL`: `https://wdwvmsrqepxvhkmodqks.supabase.co`
- `SUPABASE_ANON_KEY`: (Public client key)
- `SUPABASE_SERVICE_ROLE_KEY`: (Admin key - Backend/Scripts only)

### Google OAuth Setup
To enable Google Login:

1.  **Google Cloud Console:**
    - Project: `PolyLab`
    - Credentials: OAuth 2.0 Client ID (Web application)
    - **Authorized Redirect URI:** `https://wdwvmsrqepxvhkmodqks.supabase.co/auth/v1/callback`

2.  **Supabase Dashboard:**
    - Authentication -> Providers -> Google
    - Enabled: `True`
    - Client ID & Secret: (Copied from Google Cloud)

3.  **Redirect URLs:**
    - Supabase -> Auth -> URL Configuration
    - Site URL: `https://www.polylab.app` (Production)
    - Additional Redirect URLs: 
        - `http://127.0.0.1:8000/app`
        - `https://www.polylab.app`
        - `https://polylab.app`
        - `https://www.polylab.app/app`
        - `https://polylab.app/app`

## Product Access Direction
PolyLab auth should be treated as an account and persistence layer, not as the primary gate to the scanner.

Target model:

- Guests can access the scanner and core exploration workflow.
- Signed-in users unlock continuity features such as saved presets, saved filters, watchlists or favorites, recently viewed markets, synced preferences, and future notifications.
- If pricing is introduced later, it should be layered on top of this model rather than replacing it.

## Current Auth Touchpoints
Current frontend auth usage includes:

- email/password sign in
- Google OAuth sign in
- session restore and sign out
- login prompts on some saved-workflow style interactions

There may still be individual frontend-gated items during implementation, but the intended long-term model is:

- sign in to save and continue
- not sign in to access the basic product

## Testing
1.  Run local server: `./dev_local.sh`
2.  Open `http://127.0.0.1:8000/app`
3.  Click "Login" or trigger a sign-in prompt from an account-style action.
3.  Sign in with Google.
4.  Verify the user session is restored and the signed-in UI state updates correctly.
