# Specification: Email MCP Server

## 1. Goal
Create a Model Context Protocol (MCP) server that exposes e-mail functionality (Zoho Mail) as native tools for AI agents. This allows the agent to read, search, and send e-mails without executing external shell scripts.

## 2. Scope
*   **IMAP Tools:** 
    *   `list_unread_emails`: Returns a summary of new messages.
    *   `read_email_body`: Fetches the content of a specific e-mail.
    *   `search_emails`: Searches inbox by keyword or sender.
*   **SMTP Tools:**
    *   `send_email`: Sends a professional e-mail via Zoho SMTP.
*   **Configuration:** Uses existing credentials from `.env`.

## 3. Technical Requirements
*   **Language:** Python.
*   **Libraries:** `mcp` (Python SDK), `imaplib`, `smtplib`.
*   **Integration:** The server will be registered in the Gemini CLI environment.

## 4. Tools Definition

### 4.1 `list_unread`
*   **Inputs:** None.
*   **Output:** List of (From, Subject, Date, ID).

### 4.2 `send_message`
*   **Inputs:** `to`, `subject`, `body`.
*   **Output:** Success/Failure status.

## 5. Security
*   Credentials MUST be read from `.env`.
*   The server should handle connection timeouts gracefully.
