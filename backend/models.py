from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=False)

    city = Column(String(100), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="merchant")

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    merchant = relationship(
        "Merchant",
        back_populates="users"
    )

class ProductEconomics(Base):
    __tablename__ = "product_economics"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False, index=True)
    product_id = Column(String(50), nullable=False)
    selling_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    max_discount_percentage = Column(Float, default=10.0)
    
class ProductData(Base):
    __tablename__ = "product_data"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        String(255),
        nullable=False
    )

    product_name = Column(
        String(255),
        nullable=False
    )

    month = Column(
        String(100),
        nullable=True
    )

    unit_sales = Column(
        Integer,
        default=0
    )

    supply_time = Column(
        Integer,
        default=0
    )

    quantity_on_hand = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )