"""
WhatsApp messaging helpers for the desktop app.

Uses the official wa.me click-to-chat scheme, which opens the message
(pre-filled) in WhatsApp Desktop or WhatsApp Web. No API keys required —
the staff member just presses "send" in WhatsApp. This mirrors the behaviour
of the existing web frontend (web/js/whatsapp.js).
"""
import webbrowser
import urllib.parse
from datetime import date

from backend.utils.app_settings import load_settings


def clean_phone(phone: str, country_code: str = "212") -> str:
    """Normalise a phone number to international digits for wa.me.

    - strips spaces, dashes, parentheses, '+'
    - a leading '0' (national format) is replaced by the country code
    - if no country code is present, prepend the configured one
    """
    if not phone:
        return ""
    digits = "".join(ch for ch in str(phone) if ch.isdigit() or ch == "+")
    digits = digits.replace("+", "")

    if digits.startswith("00"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = country_code + digits[1:]
    elif not digits.startswith(country_code):
        # Bare local number without leading 0 -> assume local, add country code
        if len(digits) <= 10:
            digits = country_code + digits
    return digits


def build_wa_url(phone: str, message: str, country_code: str = "212") -> str:
    """Build a wa.me click-to-chat URL with the message pre-filled."""
    cleaned = clean_phone(phone, country_code)
    encoded = urllib.parse.quote(message or "")
    return f"https://wa.me/{cleaned}?text={encoded}"


def send_whatsapp(phone: str, message: str, country_code: str = None) -> str:
    """Open WhatsApp (Desktop/Web) with a pre-filled message. Returns the URL used."""
    if country_code is None:
        country_code = load_settings().get("country_code", "212")
    url = build_wa_url(phone, message, country_code)
    webbrowser.open(url)
    return url


def render_template(template: str, **values) -> str:
    """Safely fill a message template, ignoring unknown placeholders."""
    settings = load_settings()
    context = {
        "gym_name": settings.get("gym_name", "Gym Platform"),
        "name": "",
        "age": "",
        "days": "",
        "plan": "",
        "date": "",
    }
    context.update({k: v for k, v in values.items() if v is not None})

    class _Safe(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    try:
        return template.format_map(_Safe(context))
    except (ValueError, IndexError):
        # Malformed template -> return as-is so the user can still edit/send
        return template


def compute_age(dob: date) -> int:
    """Age in whole years as of today."""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
