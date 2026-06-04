"""
Receipt generation service
"""
from backend.utils.receipt import generate_receipt
from backend.database import get_db_session
from backend.models import Payment, Expense


def get_receipt_details(receipt_number: str) -> dict:
    """Look up receipt details"""
    db = get_db_session()
    try:
        # Check payments
        payment = db.query(Payment).filter(
            Payment.receipt_number == receipt_number
        ).first()
        if payment:
            return {
                "type": "payment",
                "receipt_number": receipt_number,
                "amount": float(payment.amount),
                "payment_type": payment.payment_type,
                "description": payment.description,
                "date": str(payment.paid_at)
            }

        # Check expenses
        expense = db.query(Expense).filter(
            Expense.receipt_number == receipt_number
        ).first()
        if expense:
            return {
                "type": "expense",
                "receipt_number": receipt_number,
                "amount": float(expense.amount),
                "category": expense.category,
                "title": expense.title,
                "description": expense.description,
                "created_by": expense.created_by,
                "date": str(expense.created_at)
            }

        return {"error": "Receipt not found"}
    finally:
        db.close()