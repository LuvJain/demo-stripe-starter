"""Order model for tracking payment status"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from datetime import datetime


class PaymentStatus(str, Enum):
    """Enum for order payment statuses"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Order(SQLModel, table=True):
    """Order model for tracking purchases and payments"""
    id: Optional[int] = Field(default=None, primary_key=True)

    # Customer info
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    customer_email: str

    # Order details
    amount: int  # Amount in cents
    currency: str = "usd"
    description: Optional[str] = None

    # Payment tracking
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_intent_id: Optional[str] = None  # Stripe payment intent ID

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_status(self, status: PaymentStatus):
        """Update order payment status and update timestamp"""
        self.payment_status = status
        self.updated_at = datetime.utcnow()