"""
Member management routes
"""
from backend.database import get_db_session
from backend.models import Member, Payment
from backend.utils.receipt import generate_receipt


def create_member(data: dict) -> dict:
    """Create new member"""
    db = get_db_session()
    try:
        member = Member(**data)
        db.add(member)
        db.flush()

        receipt = generate_receipt("GYM")
        payment = Payment(
            member_id=member.id,
            amount=data['gym_fee_paid'],
            payment_type="gym_fee",
            description=f"Plan: {data['gym_plan']}",
            receipt_number=receipt
        )
        db.add(payment)
        db.commit()
        return {"success": True, "id": member.id, "receipt": receipt}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()