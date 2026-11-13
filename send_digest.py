from pathlib import Path
from email.message import EmailMessage
import smtplib
import ssl
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--send",
    action="store_true",
    help="Send the digest email",
)
args = parser.parse_args()

gmail_address = "mouseelaine@gmail.com"

result = subprocess.run(
    [
        "/usr/bin/security",
        "find-generic-password",
        "-s", "weekly-dividend-digest",
        "-a", gmail_address,
        "-w",
    ],
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    raw = result.stdout.strip()

    # Handle Keychain's hexadecimal output when needed.
    if len(raw) == 34 and all(
        character in "0123456789abcdefABCDEF"
        for character in raw
    ):
        app_password = bytes.fromhex(raw).decode("ascii").strip()
    else:
        app_password = "".join(raw.split())

    if not (
        len(app_password) == 16
        and all("a" <= character <= "z" for character in app_password)
    ):
        raise SystemExit("Unexpected App Password format.")

    print("App Password ready for login.")

    digest_path = Path(__file__).resolve().parent / "weekly_digest.txt"
    digest_text = digest_path.read_text(encoding="utf-8")

    message = EmailMessage()
    message["Subject"] = "Weekly Dividend Digest"
    message["From"] = gmail_address
    message["To"] = gmail_address
    message.set_content(digest_text)

    print(f"Email prepared for: {message['To']}")
    print(f"Subject: {message['Subject']}")
    
    if args.send:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=context, timeout=30
        ) as server:
            print("Logging in to Gmail...")
            server.login(gmail_address, app_password)
            server.send_message(message)
            print("Gmail accepted the test email.")

        print("Check your Gmail inbox and spam folder.")
    else:
        print("Email not sent.")
else:
    print(f"Keychain lookup failed (code {result.returncode}).")
    print(result.stderr.strip())