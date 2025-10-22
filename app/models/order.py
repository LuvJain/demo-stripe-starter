"""Order model for tracking payment status via Stripe"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from datetime import datetime


class OrderStatus(str, Enum):
    """Order status enumeration for payment tracking"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


class Order(SQLModel, table=True):
    """Order model with payment tracking fields for Stripe integration"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    # Payment details
    amount: int  # In cents
    currency: str = "usd"
    description: Optional[str] = None

    # Stripe specific fields
    stripe_payment_intent_id: Optional[str] = Field(default=None, index=True)
    stripe_checkout_session_id: Optional[str] = Field(default=None, index=True)

    # Status tracking
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    error_message: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)