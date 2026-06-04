"""
Receipt number generator
"""
import uuid
from datetime import datetime


def generate_receipt(prefix: str = "RCPT") -> str:
    """Generate a unique receipt number"""
    timestamp = datetime.now().strftime("%m%d")
    unique = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{timestamp}-{unique}"