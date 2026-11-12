"""Transactional email via SMTP.

No-ops (logs only) when SMTP is not configured, so the app never fails if email
has not been set up yet. Never raises — sending email must not break a request.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def mail_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True if sent, False if SMTP is not
    configured or the send failed (the error is logged, never raised)."""
    s = get_settings()
    if not mail_configured():
        logger.info("Email not configured — would send to %s: %s", to, subject)
        return False

    msg = EmailMessage()
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as server:
            if s.smtp_tls:
                server.starttls()
            server.login(s.smtp_user, s.smtp_password)
            server.send_message(msg)
        logger.info("Sent email to %s: %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False
