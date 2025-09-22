import smtplib
from email.mime.text import MIMEText
from edge_server.config import settings


def send_email(to_email: str, subject: str, body: str):
    if not settings.SMTP_SERVER or not settings.SMTP_USER:
        print(f"[EMAIL DEBUG] To: {to_email} | Subject: {subject} | Body: {body}")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
