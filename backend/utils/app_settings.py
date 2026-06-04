"""
Persistent application settings for the desktop app.

Stores user-editable configuration (WhatsApp message templates, default
country code, automation toggles) in a JSON file next to the project so the
values survive restarts. All access goes through load_settings() / save_settings()
/ update_setting() so the rest of the app never touches the file directly.
"""
import json
import os
import threading

# settings.json lives at the project root (two levels up from this file)
_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "app_settings.json"
)

_lock = threading.Lock()

# Placeholders supported in message templates:
#   {name}  -> member full name
#   {age}   -> member age (birthday messages)
#   {days}  -> days until expiry (expiry messages)
#   {plan}  -> gym plan name
#   {date}  -> relevant date (expiry date)
DEFAULT_SETTINGS = {
    "country_code": "212",  # default international dialing code (no '+')
    "gym_name": "Gym Platform",
    "auto_birthday_enabled": True,
    "auto_expiry_enabled": True,
    "birthday_message": (
        "🎂🎉 Happy Birthday {name}! 🎉🎂\n\n"
        "Wishing you a strong and healthy year ahead! 💪🔥\n"
        "Welcome to your {age}th year!\n\n"
        "From: {gym_name} 🏋️"
    ),
    "expiry_message": (
        "Hello {name}! 👋\n\n"
        "Your {gym_name} membership ({plan}) expires on {date} "
        "— that's in {days} day(s).\n\n"
        "Renew now to keep your progress going! 💪"
    ),
    "broadcast_message": (
        "📢 {gym_name} Announcement\n\n"
        "Hello {name}! We have an exciting event coming up. "
        "Stay tuned for more details! 🏋️🔥"
    ),
}


def load_settings() -> dict:
    """Return the full settings dict, merging stored values over defaults."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        if os.path.exists(_SETTINGS_PATH):
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                settings.update(stored)
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable file -> fall back to defaults
        pass
    return settings


def save_settings(settings: dict) -> None:
    """Persist the given settings dict to disk (thread-safe)."""
    with _lock:
        with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)


def get_setting(key: str, default=None):
    """Convenience accessor for a single setting."""
    return load_settings().get(key, DEFAULT_SETTINGS.get(key, default))


def update_setting(key: str, value) -> dict:
    """Update one setting and persist. Returns the updated settings dict."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
