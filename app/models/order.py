"""Order model for tracking payment status"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PaymentStatus(str, Enum):
    """Enum representing the possible payment statuses"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Order(SQLModel, table=True):
    """Order model with payment details and status"""
    id: Optional[int] = Field(default=None, primary_key=True)

    # Payment details
    amount: int = Field(...)  # Amount in cents
    currency: str = Field(default="usd")
    payment_intent_id: Optional[str] = Field(default=None, index=True)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    # Order details
    description: Optional[str] = Field(default=None)

    # User relationship (foreign key)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def update_payment_status(self, status: PaymentStatus):
        """Update the payment status and updated_at timestamp"""
        self.payment_status = status
        self.updated_at = datetime.utcnow()