"""
Birthday routes
"""
from backend.services.birthday_service import get_today_birthdays


def get_birthdays() -> list:
    """Get today's birthdays"""
    return get_today_birthdays()