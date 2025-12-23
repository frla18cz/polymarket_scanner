from mcp.server.fastmcp import FastMCP
import imaplib
import smtplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("email")

@mcp.tool()
def list_unread_emails() -> str:
    """
    Lists unread emails from the inbox.
    Returns a string summary of unread messages.
    """
    try:
        username = os.getenv("ZOHO_EMAIL")
        password = os.getenv("ZOHO_APP_PASSWORD")
        imap_server = os.getenv("ZOHO_IMAP_SERVER", "imap.zoho.com")

        if not username or not password:
            return "Error: ZOHO_EMAIL or ZOHO_APP_PASSWORD not set in .env"

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return "No unread messages or error searching."

        email_ids = messages[0].split()
        if not email_ids:
            return "No unread messages."

        result = []
        # Fetch last 5 unread
        for e_id in email_ids[-5:]:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    result.append(f"ID: {e_id.decode()} | From: {from_} | Subject: {subject}")

        mail.close()
        mail.logout()
        return "\n".join(result)
    except Exception as e:
        return f"Error listing emails: {str(e)}"

@mcp.tool()
def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Sends an email via Zoho SMTP.
    Args:
        to_email: The recipient's email address.
        subject: The subject of the email.
        body: The plain text body of the email.
    """
    user = os.getenv("ZOHO_EMAIL")
    password = os.getenv("ZOHO_APP_PASSWORD")
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 587))

    if not all([user, password, smtp_server]):
        return "Error: ZOHO_EMAIL, ZOHO_APP_PASSWORD, or ZOHO_SMTP_SERVER not set in .env"

    msg = email.message.EmailMessage()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        return f"Email successfully sent to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool()
def search_emails(query: str) -> str:
    """
    Searches emails in the inbox by keyword (subject or sender).
    Args:
        query: The keyword to search for.
    """
    try:
        username = os.getenv("ZOHO_EMAIL")
        password = os.getenv("ZOHO_APP_PASSWORD")
        imap_server = os.getenv("ZOHO_IMAP_SERVER", "imap.zoho.com")

        if not username or not password:
            return "Error: ZOHO_EMAIL or ZOHO_APP_PASSWORD not set in .env"

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("inbox")

        # Search subject OR from. IMAP search is a bit primitive.
        # We'll try searching Subject first.
        # Constructing a valid IMAP search query for 'OR (SUBJECT query) (FROM query)'
        # Note: Some servers might be picky about complex queries. 
        # Let's try a simple subject search first as it's safer.
        status, messages = mail.search(None, f'(SUBJECT "{query}")')
        
        if status != "OK":
            return "Error searching emails."

        email_ids = messages[0].split()
        if not email_ids:
            # Try searching sender
            status, messages = mail.search(None, f'(FROM "{query}")')
            email_ids = messages[0].split()

        if not email_ids:
            return f"No emails found matching '{query}'."

        result = []
        # Fetch last 5 matches
        for e_id in email_ids[-5:]:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    result.append(f"ID: {e_id.decode()} | From: {from_} | Subject: {subject}")

        mail.close()
        mail.logout()
        return "\n".join(result)
    except Exception as e:
        return f"Error searching emails: {str(e)}"

if __name__ == "__main__":
    mcp.run()
