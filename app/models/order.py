"""Order model for tracking payment status"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PaymentStatus(str, Enum):
    """Enum for order payment status"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    """Order model with payment tracking information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    amount: int = Field(description="Amount in cents")
    currency: str = Field(default="usd")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    stripe_payment_intent_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship can be uncommented when User model has the reverse relationship
    # user: Optional["User"] = Relationship(back_populates="orders")