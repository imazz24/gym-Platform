"""
Payment history routes
"""
from backend.database import get_db_session
from backend.models import Payment, Member


def get_all_payments() -> list:
    """Get all payment records"""
    db = get_db_session()
    try:
        payments = db.query(Payment).order_by(Payment.paid_at.desc()).all()
        result = []
        for p in payments:
            member = db.query(Member).filter(Member.id == p.member_id).first()
            result.append({
                "id": p.id,
                "member_id": p.member_id,
                "member_name": member.full_name if member else "Unknown",
                "amount": float(p.amount),
                "payment_type": p.payment_type,
                "description": p.description or "",
                "receipt_number": p.receipt_number or "",
                "paid_at": str(p.paid_at) if p.paid_at else None
            })
        return result
    finally:
        db.close()