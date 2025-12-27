# Supabase Auth Setup

## Overview
PolyLab uses Supabase for authentication. Currently, it supports **Google OAuth** and **Email/Password** (via Magic Link or Password).

- **Frontend:** Implemented in `frontend_deploy/index.html` (and synced to `static/index.html`).
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
    - Site URL: `https://polylab.vercel.app` (Production)
    - Additional Redirect URLs: 
        - `http://127.0.0.1:8000` (Localhost)
        - `https://www.polylab.app`
        - `https://polylab.app`

## Premium Features (Gate)
Currently, the following features are gated on the frontend:
- **Presets:** "Warren Buffett" and "Sniper" presets require login.
- **UI:** Login modal appears when accessing these features.

## Testing
1.  Run local server: `./dev_local.sh`
2.  Click "Login" or try a locked preset.
3.  Sign in with Google.
4.  Verify "PRO" badge appears and presets unlock.
