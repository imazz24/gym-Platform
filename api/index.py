"""
Vercel serverless function - Gym Platform Web Demo
Complete Flask API with in-memory demo data
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta
import random

app = Flask(__name__)
CORS(app)

# ============ DEMO DATA ============
# In-memory storage for demo purposes

DEMO_MEMBERS = [
    {"id": 1, "full_name": "Ahmed Hassan", "phone": "+212612345678", "gym_plan": "Monthly", "start_date": "2026-05-01", "end_date": "2026-06-01", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "1995-03-15"},
    {"id": 2, "full_name": "Sara Benali", "phone": "+212698765432", "gym_plan": "Quarterly", "start_date": "2026-04-15", "end_date": "2026-07-15", "gym_fee_paid": 800, "is_active": True, "date_of_birth": "1998-07-22"},
    {"id": 3, "full_name": "Youssef Amrani", "phone": "+212655443322", "gym_plan": "Yearly", "start_date": "2026-01-01", "end_date": "2027-01-01", "gym_fee_paid": 2500, "is_active": True, "date_of_birth": "1990-11-08"},
    {"id": 4, "full_name": "Fatima Zahra", "phone": "+212677889900", "gym_plan": "Monthly", "start_date": "2026-05-20", "end_date": "2026-06-20", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "2000-02-14"},
    {"id": 5, "full_name": "Omar Tazi", "phone": "+212611223344", "gym_plan": "Weekly", "start_date": "2026-05-28", "end_date": "2026-06-04", "gym_fee_paid": 100, "is_active": False, "date_of_birth": "1988-09-30"},
    {"id": 6, "full_name": "Khadija Mourad", "phone": "+212633445566", "gym_plan": "Monthly", "start_date": "2026-05-10", "end_date": "2026-06-10", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "1996-12-05"},
    {"id": 7, "full_name": "Mehdi Alaoui", "phone": "+212644556677", "gym_plan": "Half-Year", "start_date": "2026-03-01", "end_date": "2026-09-01", "gym_fee_paid": 1500, "is_active": True, "date_of_birth": "1992-04-18"},
    {"id": 8, "full_name": "Nadia Benjelloun", "phone": "+212666778899", "gym_plan": "Monthly", "start_date": "2026-04-25", "end_date": "2026-05-25", "gym_fee_paid": 300, "is_active": False, "date_of_birth": "1999-08-11"},
]

DEMO_PRODUCTS = [
    {"id": 1, "name": "Protein Shake", "category": "Supplements", "price": 45, "stock": 25, "is_available": True},
    {"id": 2, "name": "Energy Bar", "category": "Snacks", "price": 15, "stock": 50, "is_available": True},
    {"id": 3, "name": "Gym Gloves", "category": "Accessories", "price": 80, "stock": 15, "is_available": True},
    {"id": 4, "name": "Water Bottle", "category": "Accessories", "price": 35, "stock": 30, "is_available": True},
    {"id": 5, "name": "Pre-Workout", "category": "Supplements", "price": 120, "stock": 10, "is_available": True},
    {"id": 6, "name": "Gym Towel", "category": "Accessories", "price": 25, "stock": 40, "is_available": True},
    {"id": 7, "name": "BCAA Powder", "category": "Supplements", "price": 95, "stock": 8, "is_available": True},
    {"id": 8, "name": "Resistance Band", "category": "Equipment", "price": 50, "stock": 20, "is_available": True},
]

DEMO_EXPENSES = [
    {"id": 1, "title": "Electricity Bill", "category": "Utilities", "amount": 850, "created_at": "2026-05-01", "created_by": "admin"},
    {"id": 2, "title": "Water Bill", "category": "Utilities", "amount": 200, "created_at": "2026-05-01", "created_by": "admin"},
    {"id": 3, "title": "Equipment Maintenance", "category": "Maintenance", "amount": 500, "created_at": "2026-05-15", "created_by": "admin"},
    {"id": 4, "title": "Cleaning Supplies", "category": "Supplies", "amount": 150, "created_at": "2026-05-20", "created_by": "admin"},
    {"id": 5, "title": "Internet Service", "category": "Utilities", "amount": 300, "created_at": "2026-05-01", "created_by": "admin"},
]

DEMO_PAYMENTS = [
    {"id": 1, "member_id": 1, "member_name": "Ahmed Hassan", "amount": 300, "payment_type": "gym_fee", "paid_at": "2026-05-01"},
    {"id": 2, "member_id": 2, "member_name": "Sara Benali", "amount": 800, "payment_type": "gym_fee", "paid_at": "2026-04-15"},
    {"id": 3, "member_id": 3, "member_name": "Youssef Amrani", "amount": 2500, "payment_type": "gym_fee", "paid_at": "2026-01-01"},
    {"id": 4, "member_id": 1, "member_name": "Ahmed Hassan", "amount": 45, "payment_type": "product", "paid_at": "2026-05-10"},
    {"id": 5, "member_id": 4, "member_name": "Fatima Zahra", "amount": 300, "payment_type": "gym_fee", "paid_at": "2026-05-20"},
]



# ============ ROUTES ============
# The web page is served by the static index.html at the repo root
# (Vercel serves it for "/"). This module is the JSON API only.

@app.route('/')
def index():
    """The web page is served by the static index.html (see vercel.json
    routes). This module is the JSON API; "/" only responds if hit directly."""
    return jsonify({"service": "Gym Platform API", "status": "ok", "docs": "/api/health"})


@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": "2.0", "mode": "demo"})


@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify(DEMO_MEMBERS)


@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = next((m for m in DEMO_MEMBERS if m['id'] == member_id), None)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member)


@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(DEMO_PRODUCTS)


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    return jsonify(DEMO_EXPENSES)


@app.route('/api/payments', methods=['GET'])
def get_payments():
    return jsonify(DEMO_PAYMENTS)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_members = len(DEMO_MEMBERS)
    active_members = len([m for m in DEMO_MEMBERS if m['is_active']])
    total_products = len(DEMO_PRODUCTS)
    total_revenue = sum(p['amount'] for p in DEMO_PAYMENTS)
    total_expenses = sum(e['amount'] for e in DEMO_EXPENSES)
    
    return jsonify({
        "total_members": total_members,
        "active_members": active_members,
        "total_products": total_products,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": total_revenue - total_expenses
    })


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)