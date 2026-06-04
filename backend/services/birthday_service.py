"""
Birthday detection service
"""
from datetime import date
from backend.database import get_db_session
from backend.models import Member


def get_today_birthdays() -> list:
    """Find all members whose birthday is today"""
    db = get_db_session()
    try:
        today = date.today()
        all_members = db.query(Member).filter(Member.is_active == True).all()
        birthdays = []
        for m in all_members:
            if (m.date_of_birth.month == today.month and
                m.date_of_birth.day == today.day):
                age = today.year - m.date_of_birth.year
                birthdays.append({
                    "id": m.id,
                    "full_name": m.full_name,
                    "phone_number": m.phone_number,
                    "date_of_birth": str(m.date_of_birth),
                    "age": age
                })
        return birthdays
    finally:
        db.close()


def get_upcoming_birthdays(days: int = 7) -> list:
    """Get birthdays in the next N days"""
    from datetime import timedelta
    db = get_db_session()
    try:
        today = date.today()
        all_members = db.query(Member).filter(Member.is_active == True).all()
        upcoming = []
        for m in all_members:
            try:
                this_year_bday = m.date_of_birth.replace(year=today.year)
                if this_year_bday < today:
                    this_year_bday = m.date_of_birth.replace(year=today.year + 1)
                diff = (this_year_bday - today).days
                if 0 <= diff <= days:
                    upcoming.append({
                        "id": m.id,
                        "full_name": m.full_name,
                        "phone_number": m.phone_number,
                        "days_until": diff,
                        "birthday_date": str(this_year_bday)
                    })
            except ValueError:
                continue
        return sorted(upcoming, key=lambda x: x["days_until"])
    finally:
        db.close()