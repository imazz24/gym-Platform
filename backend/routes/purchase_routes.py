"""
Purchase management routes
"""
from backend.database import get_db_session
from backend.models import Purchase, Product, Payment
from backend.utils.receipt import generate_receipt


def create_purchase(member_id: int, product_id: int, quantity: int, purchased_by: str) -> dict:
    """Create a purchase"""
    db = get_db_session()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product or product.stock < quantity:
            return {"success": False, "message": "Insufficient stock"}

        total = float(product.price) * quantity
        receipt = generate_receipt("PUR")

        purchase = Purchase(
            member_id=member_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total,
            purchased_by=purchased_by
        )
        db.add(purchase)
        product.stock -= quantity

        payment = Payment(
            member_id=member_id,
            amount=total,
            payment_type="product",
            description=f"{product.name} x{quantity}",
            receipt_number=receipt
        )
        db.add(payment)
        db.commit()
        return {"success": True, "total": total, "receipt": receipt}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()