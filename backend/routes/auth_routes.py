"""
Authentication routes
"""
from backend.utils.auth import verify_password, get_password_hash, create_token
from backend.database import get_db_session
from backend.models import SystemUser


def authenticate(username: str, password: str) -> dict:
    """Authenticate a user"""
    db = get_db_session()
    try:
        user = db.query(SystemUser).filter(
            SystemUser.username == username,
            SystemUser.is_active == True
        ).first()

        if user and verify_password(password, user.hashed_password):
            token = create_token({
                "sub": user.username,
                "role": user.role,
                "name": user.full_name
            })
            return {
                "success": True,
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }
        return {"success": False, "message": "Invalid credentials"}
    finally:
        db.close()