"""
Helper utilities
"""
from datetime import date, timedelta


def calculate_age(birth_date: date) -> int:
    """Calculate age from date of birth"""
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def days_until(target_date: date) -> int:
    """Calculate days until a target date"""
    return (target_date - date.today()).days


def days_overdue(target_date: date) -> int:
    """Calculate how many days overdue"""
    return (date.today() - target_date).days


def format_currency(amount: float) -> str:
    """Format as currency"""
    return f"${amount:,.2f}"


def get_plan_price(plan: str) -> float:
    """Get price for gym plan"""
    plans = {
        "3_days_50": 50.0,
        "all_days_60": 60.0
    }
    return plans.get(plan, 0.0)


def get_activity_price(activity: str) -> float:
    """Get price for activity"""
    activities = {
        "zumba_40": 40.0,
        "boxing_50": 50.0,
        "yoga_35": 35.0,
        "crossfit_45": 45.0
    }
    return activities.get(activity, 0.0)