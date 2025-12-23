# Plan: Project Launch Preparation

## Phase 1: Operational Setup
- [ ] Task: Research and Select Email Provider
    -   *Context:* Evaluate options like Google Workspace (paid), Zoho (free tier), or Cloudflare Email Routing (free forwarding).
    -   *Action:* Decide on a provider and set up `hello@polylab.app` (or similar).
- [ ] Task: Configure DNS Records
    -   *Context:* Required for email delivery (MX, SPF, DKIM).
    -   *Action:* Update DNS settings at the domain registrar.
- [ ] Task: Conductor - User Manual Verification 'Operational Setup' (Protocol in workflow.md)

## Phase 2: Content Creation (Legal & FAQ)
- [x] Task: Draft Privacy Policy
    -   *Context:* Need a standard policy covering analytics and auth.
    -   *Action:* Draft text using a standard template suitable for a non-commercial/freemium web app.
- [x] Task: Draft Terms of Service
    -   *Context:* Critical disclaimer: "Not Financial Advice".
    -   *Action:* Draft text emphasizing the analytical nature of the tool.
- [x] Task: Write FAQ Content
    -   *Context:* Address the 5 key questions identified in the spec.
    -   *Action:* Write clear, concise answers in markdown format.
- [ ] Task: Conductor - User Manual Verification 'Content Creation' (Protocol in workflow.md)

## Phase 3: Frontend Implementation
- [x] Task: Design Footer Component
    -   *Context:* The footer is the standard place for Legal/Contact links.
    -   *Action:* Update `index.html` to include a footer with links to FAQ, Privacy, Terms, and Contact.
- [x] Task: Implement FAQ Modal/Section
    -   *Context:* A dedicated area for user questions.
    -   *Action:* Create a Vue.js component (or HTML section) for the FAQ with accordion functionality.
- [x] Task: Implement Legal Pages (Modals or Views)
    -   *Context:* Display the drafted legal text.
    -   *Action:* Create views for Privacy Policy and ToS.
- [ ] Task: Verify Links and Responsive Design
    -   *Context:* Ensure all new content is accessible on mobile and desktop.
    -   *Action:* Test the footer links and content display.
- [ ] Task: Conductor - User Manual Verification 'Frontend Implementation' (Protocol in workflow.md)
