# Plan: Polymarket Outreach & Launch

## Phase 1: Operational Setup (Email)
- [x] Task: Research and Select Email Provider
    -   *Context:* Evaluate options (Google Workspace, Zoho, Cloudflare Email Routing) for `hello@polylab.app`.
    -   *Action:* Set up on Zoho.
- [x] Task: Configure DNS Records
    -   *Context:* Required for email delivery (MX, SPF, DKIM) to ensure high deliverability to Polymarket team.
    -   *Action:* DNS configured and verified.
- [x] Task: Verify Email Delivery
    -   *Action:* Access verified via `check_emails.py` and `send_email.py`.

## Phase 2: Pitch Preparation [checkpoint: 1a41ab0]
- [x] Task: SEO & Social Meta Tags
    -   *Context:* Ensure shared links look professional.
    -   *Action:* Updated `index.html` with OG tags and description.
- [x] Task: Revamp README
    -   *Context:* Serve as a landing page for devs/technical reviewers.
    -   *Action:* Rewrote README.md with clear features and tech stack.
- [x] Task: Draft Outreach Email
    -   *Context:* The initial contact with Polymarket.
    -   *Action:* Drafted `docs/PITCH_DRAFT.md`.
- [~] Task: Create Demo Asset (GIF/Video)
    -   *Context:* Use Playwright to automate the UI and capture a demo GIF.
    -   *Action:* Implement `generate_demo.py` using Playwright and produce `static/assets/demo.gif`.

## Phase 3: Execution
- [~] Task: Deploy to Production
    -   *Context:* Ensure all changes (meta tags, footer) are live on `polylab.app`.
    -   *Action:* Push to main and verify Vercel deployment.
- [ ] Task: Send Email to Polymarket
    -   *Action:* Send the finalized email to `hello@polymarket.com`.
- [ ] Task: Community Launch (Twitter/Discord)
    -   *Action:* Post in Polymarket Discord #dev-projects and tweet with relevant tags.
