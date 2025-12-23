import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

def get_unread_emails():
    user = os.getenv("ZOHO_EMAIL")
    password = os.getenv("ZOHO_APP_PASSWORD")
    imap_url = os.getenv("ZOHO_IMAP_SERVER")

    if not all([user, password, imap_url]):
        print("Error: Email credentials missing in .env")
        return

    try:
        # Connect to server
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select("INBOX")

        # Search for unread emails (status UNSEEN)
        status, response = mail.search(None, 'UNSEEN')
        unread_msg_nums = response[0].split()

        print(f"--- Unread Emails for {user} ---")
        print(f"Total unread: {len(unread_msg_nums)}\n")

        for num in unread_msg_nums:
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

            print(f"From: {from_}")
            print(f"Subject: {subject}")
            print("-" * 30)

        mail.logout()
    except Exception as e:
        print(f"Error accessing mail: {e}")

if __name__ == "__main__":
    get_unread_emails()
