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
    *   Open `static/index.html`.
    *   Find the configuration at the top of the script:
    ```javascript
    const API_BASE_URL = "http://YOUR_VPS_IP"; // Change this!
    ```
    *   Replace `http://localhost:8000` with your actual VPS IP address or domain (e.g., `http://34.123.45.67` or `https://api.polyscan.xyz`).
    *   *Note:* If your VPS does not have SSL (HTTPS), you might run into "Mixed Content" issues if Vercel serves over HTTPS. It is highly recommended to set up HTTPS on the VPS (Caddy handles this automatically if you point a domain to it).

2.  **Deploy to Vercel:**
    *   **Option A (CLI):** Run `vercel deploy` inside the `static/` folder.
    *   **Option B (Git):** Create a new generic Git repo containing just `index.html` (or point Vercel to the `static` folder of this repo) and connect it to Vercel.

## 3. Verify

1.  Open your Vercel URL.
2.  Open the browser console (F12).
3.  Check if network requests to `YOUR_VPS_IP/api/markets` are successful.
