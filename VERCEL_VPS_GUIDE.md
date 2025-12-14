# Guide: Split Architecture (Vercel + VPS)

This guide explains how to deploy the application with the Frontend hosted on **Vercel** and the Backend (API + Scraper) on a **Google Cloud VPS**.

## 1. Backend Deployment (Google Cloud VPS)

The backend handles the data, scraping, and API. It no longer serves the HTML.

1.  **SSH into your VPS.**
2.  **Pull this branch:**
    ```bash
    git checkout feature/vercel-split
    git pull origin feature/vercel-split
    ```
3.  **Update settings:**
    *   In `main.py`, update the `origins` list in the CORS configuration if you have a custom domain for Vercel.
    ```python
    origins = [
        "https://your-project.vercel.app", 
        "https://polymarket-scanner.vercel.app"
    ]
    ```
4.  **Deploy:**
    ```bash
    docker-compose up -d --build
    ```
    Your API will be available at `http://YOUR_VPS_IP/api/...`.

## 2. Frontend Deployment (Vercel)

The frontend is a single static HTML file.

1.  **Prepare the file:**
    *   The canonical source is `frontend_deploy/index.html` (and `static/index.html` must stay identical).
    *   Find the configuration at the top of the script:
    ```javascript
    const API_BASE_URL = "";
    ```
    *   Recommended: keep `API_BASE_URL` empty and use a Vercel rewrite/proxy so the frontend can call `/api/*` on its own origin.
    *   If you cannot use rewrites/proxying, set `API_BASE_URL` to your API origin (e.g. `https://api.polyscan.xyz`) and make sure the backend has correct CORS + HTTPS.

2.  **Deploy to Vercel:**
    *   **Option A (recommended):** Deploy from the repo root so `vercel.json` rewrites apply (frontend calls `/api/*` on the same origin).
    *   **Option B (static-only):** Deploy only `static/index.html` (or a minimal repo containing it). In that case you typically need to set `API_BASE_URL` and handle CORS/HTTPS, unless you also add rewrites to that project.

## 3. Verify

1.  Open your Vercel URL.
2.  Open the browser console (F12).
3.  Check if network requests to `YOUR_VPS_IP/api/markets` are successful.
