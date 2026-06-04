"""
Finance routes
"""
from backend.services.profit_service import (
    calculate_monthly_profit,
    calculate_total_profit,
    get_revenue_by_type,
    get_expenses_by_category
)


def get_finance_data() -> dict:
    """Get all financial data"""
    monthly = calculate_monthly_profit()
    total = calculate_total_profit()
    revenue_types = get_revenue_by_type()
    expense_categories = get_expenses_by_category()

    return {
        "monthly": monthly,
        "total": total,
        "revenue_by_type": revenue_types,
        "expenses_by_category": expense_categories
    }