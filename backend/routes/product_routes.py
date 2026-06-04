"""
Product management routes
"""
from backend.database import get_db_session
from backend.models import Product


def get_all_products() -> list:
    """Get all available products"""
    db = get_db_session()
    try:
        products = db.query(Product).filter(Product.is_available == True).all()
        return [{
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": float(p.price),
            "stock": p.stock
        } for p in products]
    finally:
        db.close()