"""Order model for tracking payments"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from datetime import datetime


class PaymentStatus(str, Enum):
    """Payment status enum for orders"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Order(SQLModel, table=True):
    """Order model with payment tracking"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    payment_intent_id: Optional[str] = Field(default=None, index=True)
    amount: int = Field()  # Amount in cents
    currency: str = Field(default="usd")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Metadata
    metadata: Optional[str] = Field(default=None)  # JSON string for additional data

    # Relationship to User - not fully implemented in this story
    # user: Optional["User"] = Relationship(back_populates="orders")