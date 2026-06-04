"""
Membership expiration monitoring service
"""
from datetime import date, timedelta
from backend.database import get_db_session
from backend.models import Member


def get_expiring_members(days: int = 7) -> list:
    """Get members expiring within N days"""
    db = get_db_session()
    try:
        today = date.today()
        threshold = today + timedelta(days=days)
        members = db.query(Member).filter(
            Member.is_active == True,
            Member.end_date >= today,
            Member.end_date <= threshold,
            Member.renewal_notified == False
        ).all()
        result = []
        for m in members:
            days_left = (m.end_date - today).days
            result.append({
                "id": m.id,
                "full_name": m.full_name,
                "phone_number": m.phone_number,
                "end_date": str(m.end_date),
                "days_left": days_left,
                "gym_plan": m.gym_plan
            })
        return result
    finally:
        db.close()


def get_expired_members() -> list:
    """Get members whose membership has expired"""
    db = get_db_session()
    try:
        today = date.today()
        members = db.query(Member).filter(
            Member.is_active == True,
            Member.end_date < today
        ).all()
        result = []
        for m in members:
            days_over = (today - m.end_date).days
            result.append({
                "id": m.id,
                "full_name": m.full_name,
                "phone_number": m.phone_number,
                "end_date": str(m.end_date),
                "days_over": days_over
            })
        return result
    finally:
        db.close()


def check_and_alert() -> dict:
    """Check expirations and return alert status"""
    expired = get_expired_members()
    expiring = get_expiring_members(7)
    return {
        "expired_count": len(expired),
        "expiring_count": len(expiring),
        "expired": expired,
        "expiring": expiring,
        "has_alerts": len(expired) > 0 or len(expiring) > 0
    }