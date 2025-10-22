"""User model - ready for subscription fields to be added"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class User(SQLModel, table=True):
    """Basic user model without subscription fields"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

    # Subscription fields will be added by the implementation story

    # Relationship with orders
    orders: List["Order"] = Relationship(back_populates="user")
