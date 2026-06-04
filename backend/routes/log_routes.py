"""
Employee activity log routes
"""
from backend.database import get_db_session
from backend.models import EmployeeLog


def get_logs(limit: int = 100) -> list:
    """Get employee logs"""
    db = get_db_session()
    try:
        logs = db.query(EmployeeLog).order_by(
            EmployeeLog.created_at.desc()
        ).limit(limit).all()
        return [{
            "id": l.id,
            "employee_username": l.employee_username,
            "action": l.action,
            "created_at": str(l.created_at) if l.created_at else None
        } for l in logs]
    finally:
        db.close()


def add_log(username: str, action: str):
    """Add a log entry"""
    db = get_db_session()
    try:
        log = EmployeeLog(employee_username=username, action=action)
        db.add(log)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()