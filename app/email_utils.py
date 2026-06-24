import smtplib
from email.message import EmailMessage

from app.config import settings


def send_email(subject: str, body: str, to_email: str) -> bool:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password or not settings.email_from:
        if settings.app_env.lower() != "development":
            return False
        print(
            f"[LEVERAGE] SMTP not configured. Skipping email send in local/dev mode."
            f"\nTo: {to_email}\nSubject: {subject}\n\n{body}"
        )
        return True

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
        return True
    except Exception:
        return False
