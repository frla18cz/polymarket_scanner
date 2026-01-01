import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

def send_email(to_email, subject, body):
    user = os.getenv("ZOHO_EMAIL")
    password = os.getenv("ZOHO_APP_PASSWORD")
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 587))

    if not all([user, password, smtp_server]):
        print("Error: Email credentials missing in .env")
        return False

    # Create message
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Secure the connection
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        print(f"Email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # CLI Mode
        if len(sys.argv) < 4:
            print("Usage: python send_email.py <to> <subject> <body>")
            sys.exit(1)
        send_email(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Test execution
        TEST_RECIPIENT = os.getenv("ZOHO_EMAIL") # Send to yourself for testing
        send_email(
            TEST_RECIPIENT, 
            "PolyLab AI Test", 
            "Hello! This is a test email sent by the PolyLab AI Agent via Zoho SMTP."
        )
