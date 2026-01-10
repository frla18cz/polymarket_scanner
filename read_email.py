import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

def get_email_body(email_id):
    user = os.getenv("ZOHO_EMAIL")
    password = os.getenv("ZOHO_APP_PASSWORD")
    imap_url = os.getenv("ZOHO_IMAP_SERVER", "imap.zoho.com")

    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user, password)
    mail.select("INBOX")

    status, data = mail.fetch(str(email_id), '(RFC822)')
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)

    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    
    from_, encoding = decode_header(msg.get("From"))[0]
    if isinstance(from_, bytes):
        from_ = from_.decode(encoding if encoding else "utf-8")

    print(f"From: {from_}")
    print(f"Subject: {subject}")
    print("-" * 30)

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                print(payload.decode())
    else:
        payload = msg.get_payload(decode=True)
        print(payload.decode())

    mail.logout()

if __name__ == "__main__":
    import sys
    id_to_read = sys.argv[1] if len(sys.argv) > 1 else 7
    get_email_body(id_to_read)
