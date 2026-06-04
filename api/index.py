"""
Vercel serverless function entrypoint
Flask API wrapper for the Gym Platform backend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path for backend imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db_session
from backend.models import Member, Payment, Product, Purchase, Expense, SystemUser
from backend.utils.auth import verify_password, get_password_hash, create_token

app = Flask(__name__)
CORS(app)

# Initialize database on startup
init_db()


@app.route('/')
def index():
    return jsonify({
        "name": "Gym Platform API",
        "version": "2.0",
        "status": "running",
        "endpoints": [
            "/api/health",
            "/api/members",
            "/api/products",
            "/api/payments",
        ]
    })


@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/members', methods=['GET'])
def get_members():
    db = get_db_session()
    try:
        members = db.query(Member).all()
        return jsonify([{
            "id": m.id,
            "full_name": m.full_name,
            "phone": m.phone,
            "gym_plan": m.gym_plan,
            "start_date": str(m.start_date) if m.start_date else None,
            "end_date": str(m.end_date) if m.end_date else None,
            "is_active": m.is_active
        } for m in members])
    finally:
        db.close()


@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    db = get_db_session()
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return jsonify({"error": "Member not found"}), 404
        return jsonify({
            "id": member.id,
            "full_name": member.full_name,
            "phone": member.phone,
            "gym_plan": member.gym_plan,
            "start_date": str(member.start_date) if member.start_date else None,
            "end_date": str(member.end_date) if member.end_date else None,
            "is_active": member.is_active
        })
    finally:
        db.close()


@app.route('/api/products', methods=['GET'])
def get_products():
    db = get_db_session()
    try:
        products = db.query(Product).all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "price": float(p.price) if p.price else 0,
            "stock": p.stock,
            "category": p.category
        } for p in products])
    finally:
        db.close()


@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db_session()
    try:
        total_members = db.query(Member).count()
        active_members = db.query(Member).filter(Member.is_active == True).count()
        total_products = db.query(Product).count()
        
        return jsonify({
            "total_members": total_members,
            "active_members": active_members,
            "total_products": total_products
        })
    finally:
        db.close()


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)