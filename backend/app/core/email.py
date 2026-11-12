"""Transactional email (password reset, invites).

Two delivery backends, chosen automatically:

1. Resend HTTP API (preferred) — used when ``resend_api_key`` is set. Sends over
   HTTPS/443, so it works on hosts that block outbound SMTP ports (Railway,
   Render, Fly all block 25/465/587). This is the reliable production path.
2. SMTP (fallback) — used when Resend is not configured but SMTP is. Forced over
   IPv4, since container platforms often lack an IPv6 route. Kept for self-hosted
   or local setups; will time out on hosts that block SMTP ports.

Sending never raises — a failed email must not break the request. When neither
backend is configured the app logs what it would have sent and returns False.
"""

from __future__ import annotations

import logging
import smtplib
import socket
import ssl
from email.message import EmailMessage

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


def resend_configured() -> bool:
    return bool(get_settings().resend_api_key)


def smtp_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password)


def mail_configured() -> bool:
    """True when any email backend is usable."""
    return resend_configured() or smtp_configured()


# --- Resend (HTTP) --------------------------------------------------------- #


def _send_resend(to: str, subject: str, body: str) -> bool:
    s = get_settings()
    resp = httpx.post(
        RESEND_ENDPOINT,
        headers={"Authorization": f"Bearer {s.resend_api_key}"},
        json={"from": s.resend_from, "to": [to], "subject": subject, "text": body},
        timeout=20,
    )
    if resp.status_code >= 400:
        # Surface the provider message (never contains the key) for logs.
        logger.error("Resend rejected email to %s (%s): %s", to, resp.status_code, resp.text)
        return False
    logger.info("Sent email to %s via Resend: %s", to, subject)
    return True


# --- SMTP (fallback) ------------------------------------------------------- #


def _smtp_connect() -> smtplib.SMTP:
    """Open an authenticated SMTP connection, forcing IPv4 and validating TLS
    against the configured hostname (even though we dial the resolved IPv4)."""
    s = get_settings()
    info = socket.getaddrinfo(s.smtp_host, s.smtp_port, socket.AF_INET, socket.SOCK_STREAM)
    ipv4 = info[0][4][0]

    server = smtplib.SMTP(timeout=20)
    server.connect(ipv4, s.smtp_port)
    server.ehlo(s.smtp_host)
    if s.smtp_tls:
        server._host = s.smtp_host  # type: ignore[attr-defined]
        server.starttls(context=ssl.create_default_context())
        server.ehlo(s.smtp_host)
    server.login(s.smtp_user, s.smtp_password)
    return server


def _send_smtp(to: str, subject: str, body: str) -> bool:
    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    server = _smtp_connect()
    try:
        server.send_message(msg)
    finally:
        server.quit()
    logger.info("Sent email to %s via SMTP: %s", to, subject)
    return True


# --- Public API ------------------------------------------------------------ #


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via the configured backend. Returns True on
    success, False if no backend is configured or the send failed (errors are
    logged, never raised)."""
    if resend_configured():
        try:
            return _send_resend(to, subject, body)
        except Exception:
            logger.exception("Failed to send email to %s via Resend", to)
            return False

    if smtp_configured():
        try:
            return _send_smtp(to, subject, body)
        except Exception:
            logger.exception("Failed to send email to %s via SMTP", to)
            return False

    logger.info("Email not configured — would send to %s: %s", to, subject)
    return False


def mail_diagnose() -> dict[str, object]:
    """Report which backend is active and whether it can reach its provider,
    without sending a real email or ever exposing a secret."""
    s = get_settings()
    if resend_configured():
        base: dict[str, object] = {"backend": "resend", "from": s.resend_from}
        try:
            # HEAD the API host to confirm outbound HTTPS works (no email sent).
            httpx.get("https://api.resend.com", timeout=10)
            return {**base, "configured": True, "reachable": True, "error": None}
        except Exception as exc:  # noqa: BLE001
            return {**base, "configured": True, "reachable": False, "error": f"{type(exc).__name__}: {exc}"}

    if smtp_configured():
        base = {"backend": "smtp", "host": s.smtp_host, "port": s.smtp_port, "user": s.smtp_user}
        try:
            server = _smtp_connect()
            server.quit()
            return {**base, "configured": True, "reachable": True, "error": None}
        except Exception as exc:  # noqa: BLE001
            return {**base, "configured": True, "reachable": False, "error": f"{type(exc).__name__}: {exc}"}

    return {"backend": None, "configured": False, "reachable": False, "error": "No email backend configured"}
