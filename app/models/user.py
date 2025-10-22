"""User model with subscription fields"""
from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    """User model with subscription fields for Stripe integration"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

    # Subscription fields
    subscription_status: Optional[str] = None
    subscription_tier: Optional[str] = None
    stripe_customer_id: Optional[str] = None
