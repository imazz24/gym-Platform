"""
Expense management routes
"""
from backend.database import get_db_session
from backend.models import Expense
from backend.utils.receipt import generate_receipt


def create_expense(data: dict) -> dict:
    """Create new expense"""
    db = get_db_session()
    try:
        receipt = generate_receipt("EXP")
        expense = Expense(
            title=data['title'],
            description=data.get('description', ''),
            amount=data['amount'],
            category=data['category'],
            receipt_number=receipt,
            created_by=data['created_by']
        )
        db.add(expense)
        db.commit()
        return {"success": True, "receipt_number": receipt}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()