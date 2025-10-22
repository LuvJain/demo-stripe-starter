"""Order model for tracking payment status"""
from enum import Enum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User


class OrderStatus(str, Enum):
    """Status of an order payment"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(SQLModel, table=True):
    """Order model for tracking payment status"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="orders")

    # Payment information
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(default="usd")
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    # Stripe-specific fields
    stripe_payment_intent_id: Optional[str] = Field(
        default=None, index=True, description="Stripe payment intent ID"
    )
    stripe_payment_method_id: Optional[str] = Field(
        default=None, description="Stripe payment method ID"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Metadata
    description: Optional[str] = Field(default=None, description="Order description")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")