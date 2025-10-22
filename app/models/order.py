"""Order model for tracking payment status"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, ForwardRef
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status enum for tracking the state of an order payment"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Order(SQLModel, table=True):
    """
    Order model for tracking purchases and their payment status
    Updated by webhook handlers when payment events are received from Stripe
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    stripe_payment_intent_id: Optional[str] = Field(default=None, index=True)
    amount: int = Field(...)  # Amount in cents
    currency: str = Field(default="usd")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user (will be linked when User subscription fields are added)
    # user: Optional["User"] = Relationship(back_populates="orders")