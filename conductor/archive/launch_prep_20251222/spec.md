# Specification: Project Launch Preparation

## 1. Goal
Establish the operational and content foundation necessary for a professional project launch. This includes setting up communication channels, creating essential user documentation (FAQ), and ensuring basic legal compliance.

## 2. Scope
*   **Professional Email:** Setup a domain-based email address (e.g., `hello@polylab.app` or similar) to establish trust.
*   **FAQ Section:** Create a "Frequently Asked Questions" section on the frontend to address common user queries (methodology, data freshness, costs).
*   **Legal Pages:** Add standard "Privacy Policy" and "Terms of Service" pages to protect the project and inform users.
*   **About Section:** (Optional) A brief section explaining the "Why" behind PolyLab.

## 3. Requirements

### 3.1 Email Setup
*   **Provider:** Evaluate and select a provider (e.g., Google Workspace, Zoho, or forwarding via Cloudflare/Registrar).
*   **Address:** Create generic contact alias (e.g., `support@` or `hello@`).
*   **Integration:** Ensure email is listed on the site.

### 3.2 FAQ Content
*   **Format:** Accordion-style or list-based UI component.
*   **Key Questions to Answer:**
    *   What is PolyLab?
    *   How is APR calculated?
    *   Why is data updated hourly?
    *   Is it free?
    *   Are you affiliated with Polymarket?

### 3.3 Legal Compliance
*   **Privacy Policy:** State what data is collected (cookies, analytics, auth).
*   **Terms of Service:** Disclaimer that this is an analytics tool, not financial advice.
*   **Location:** accessible via footer links.

## 4. Design & UX
*   **FAQ:** Clean, readable text with expandable answers to save space.
*   **Legal:** Simple text pages, linked unobtrusively from the footer.
*   **Styling:** Consistent with existing Tailwind CSS theme.

## 5. Technical Implementation
*   **Frontend:** Add new routes or modal components for these sections in `index.html`.
*   **Routing:** Ensure the single-page app handles these "pages" correctly (e.g., anchor links or simple view switching).
