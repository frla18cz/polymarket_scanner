import imaplib
import email
from email.header import decode_header
import os
import sys
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

def get_mail_connection():
    user = os.getenv("ZOHO_EMAIL")
    password = os.getenv("ZOHO_APP_PASSWORD")
    imap_url = os.getenv("ZOHO_IMAP_SERVER", "imap.zoho.com")

    if not all([user, password, imap_url]):
        print("Error: Email credentials missing in .env")
        return None

    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select("INBOX")
        return mail
    except Exception as e:
        print(f"Error connecting to mail: {e}")
        return None

def display_emails(mail, email_ids, title="Emails"):
    print(f"--- {title} ---")
    if not email_ids:
        print("No emails found.\n")
        return

    print(f"Total: {len(email_ids)}\n")
    # Show last 10
    for num in email_ids[-10:]:
        status, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        # Decode from
        from_, encoding = decode_header(msg.get("From"))[0]
        if isinstance(from_, bytes):
            from_ = from_.decode(encoding if encoding else "utf-8")

        print(f"ID: {num.decode()} | From: {from_}")
        print(f"Subject: {subject}")
        print("-" * 30)

def list_unread():
    mail = get_mail_connection()
    if not mail: return
    
    status, response = mail.search(None, 'UNSEEN')
    unread_ids = response[0].split()
    display_emails(mail, unread_ids, "Unread Emails")
    mail.logout()

def search_emails(query):
    mail = get_mail_connection()
    if not mail: return
    
    # Search subject
    status, response = mail.search(None, f'(SUBJECT "{query}")')
    ids = response[0].split()
    
    if not ids:
        # Search from
        status, response = mail.search(None, f'(FROM "{query}")')
        ids = response[0].split()
        
    display_emails(mail, ids, f"Search Results for '{query}'")
    mail.logout()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_emails(" ".join(sys.argv[1:]))
    else:
        list_unread()