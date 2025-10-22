"""User model with subscription fields for Stripe integration"""
from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    """User model with subscription fields for Stripe integration"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

    # Subscription fields for Stripe integration
    subscription_status: Optional[str] = Field(default=None, description="Current subscription status (e.g., active, inactive, canceled)")
    subscription_tier: Optional[str] = Field(default=None, description="Subscription tier or plan level")
    stripe_customer_id: Optional[str] = Field(default=None, description="Stripe customer ID for payment processing")
