"""Transactional email via SMTP.

No-ops (logs only) when SMTP is not configured, so the app never fails if email
has not been set up yet. Never raises — sending email must not break a request.

Connections are forced over IPv4: container platforms (e.g. Railway) often lack
an IPv6 route, which surfaces as "[Errno 101] Network is unreachable" when the
SMTP host resolves to an IPv6 address first.
"""

from __future__ import annotations

import logging
import smtplib
import socket
import ssl
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def mail_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password)


def _connect() -> smtplib.SMTP:
    """Open an authenticated SMTP connection, forcing IPv4 and validating TLS
    against the configured hostname (even though we dial the resolved IPv4)."""
    s = get_settings()
    info = socket.getaddrinfo(s.smtp_host, s.smtp_port, socket.AF_INET, socket.SOCK_STREAM)
    ipv4 = info[0][4][0]

    server = smtplib.SMTP(timeout=20)
    server.connect(ipv4, s.smtp_port)
    server.ehlo(s.smtp_host)
    if s.smtp_tls:
        # Validate the certificate against the real hostname, not the IP we dialed.
        server._host = s.smtp_host  # type: ignore[attr-defined]
        server.starttls(context=ssl.create_default_context())
        server.ehlo(s.smtp_host)
    server.login(s.smtp_user, s.smtp_password)
    return server


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True if sent, False if SMTP is not
    configured or the send failed (the error is logged, never raised)."""
    if not mail_configured():
        logger.info("Email not configured — would send to %s: %s", to, subject)
        return False

    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        server = _connect()
        try:
            server.send_message(msg)
        finally:
            server.quit()
        logger.info("Sent email to %s: %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False


def smtp_diagnose() -> dict[str, object]:
    """Connect + log in to SMTP (no email sent) and report the result. Surfaces
    the exact provider error for debugging without ever exposing the password."""
    s = get_settings()
    if not mail_configured():
        return {"configured": False, "ok": False, "error": "SMTP not configured"}
    base = {"configured": True, "host": s.smtp_host, "port": s.smtp_port, "user": s.smtp_user}
    try:
        server = _connect()
        server.quit()
        return {**base, "ok": True, "error": None}
    except Exception as exc:  # noqa: BLE001 — surface any provider error
        return {**base, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
