"""
Employee management routes
"""
from backend.database import get_db_session
from backend.models import SystemUser
from backend.utils.auth import get_password_hash


def create_employee(data: dict) -> dict:
    """Create new employee"""
    db = get_db_session()
    try:
        existing = db.query(SystemUser).filter(
            SystemUser.username == data['username']
        ).first()
        if existing:
            return {"success": False, "message": "Username exists"}

        employee = SystemUser(
            username=data['username'],
            hashed_password=get_password_hash(data['password']),
            full_name=data['full_name'],
            role="employee",
            salary=data.get('salary', 0),
            working_days=data.get('working_days', 0)
        )
        db.add(employee)
        db.commit()
        return {"success": True, "id": employee.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()