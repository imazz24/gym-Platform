"""
SQLAlchemy ORM Models for Gym Platform
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    Date, DateTime, Text, ForeignKey, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class SystemUser(Base):
    __tablename__ = "system_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' or 'employee'
    is_active = Column(Boolean, default=True)

    # Employee details
    salary = Column(Float, default=0.0)
    working_days = Column(Integer, default=0)
    hire_date = Column(Date, default=None)
    phone = Column(String(20), default="")
    address = Column(String(255), default="")
    notes = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    photo = Column(LargeBinary, nullable=True)
    date_of_birth = Column(Date, nullable=False)
    phone_number = Column(String(20), nullable=False)
    support_phone_number = Column(String(20), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    gym_plan = Column(String(50), nullable=False)
    gym_fee_paid = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    renewal_notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    activities = relationship("MemberActivity", back_populates="member", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="member", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="member", cascade="all, delete-orphan")


class MemberActivity(Base):
    __tablename__ = "member_activities"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    fee = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    member = relationship("Member", back_populates="activities")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

    purchases = relationship("Purchase", back_populates="product")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    purchased_by = Column(String(100), default="")
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())

    member = relationship("Member", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    receipt_number = Column(String(100), unique=True, nullable=True)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())

    member = relationship("Member", back_populates="payments")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    receipt_number = Column(String(100), unique=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class EmployeeLog(Base):
    __tablename__ = "employee_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=True)
    employee_username = Column(String(100), nullable=False)
    action = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())