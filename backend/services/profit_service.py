"""
Financial profit calculation service
"""
from datetime import date, datetime, timedelta
from sqlalchemy import func
from backend.database import get_db_session
from backend.models import Payment, Expense


def calculate_monthly_profit(year=None, month=None) -> dict:
    """Calculate profit for a specific month"""
    db = get_db_session()
    try:
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        # Revenue
        revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.paid_at >= start,
            Payment.paid_at < end
        ).scalar()

        # Expenses
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.created_at >= start,
            Expense.created_at < end
        ).scalar()

        return {
            "year": year,
            "month": month,
            "revenue": float(revenue),
            "expenses": float(expenses),
            "profit": float(revenue) - float(expenses)
        }
    finally:
        db.close()


def calculate_total_profit() -> dict:
    """Calculate all-time profit"""
    db = get_db_session()
    try:
        revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()

        return {
            "total_revenue": float(revenue),
            "total_expenses": float(expenses),
            "total_profit": float(revenue) - float(expenses)
        }
    finally:
        db.close()


def get_revenue_by_type() -> list:
    """Breakdown revenue by payment type"""
    db = get_db_session()
    try:
        results = db.query(
            Payment.payment_type,
            func.sum(Payment.amount)
        ).group_by(Payment.payment_type).all()

        return [{
            "type": r[0],
            "amount": float(r[1])
        } for r in results]
    finally:
        db.close()


def get_expenses_by_category() -> list:
    """Breakdown expenses by category"""
    db = get_db_session()
    try:
        results = db.query(
            Expense.category,
            func.sum(Expense.amount)
        ).group_by(Expense.category).all()

        return [{
            "category": r[0],
            "amount": float(r[1])
        } for r in results]
    finally:
        db.close()