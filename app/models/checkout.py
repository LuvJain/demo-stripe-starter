"""
Checkout models for the Stripe integration.
Contains request and response models for the checkout endpoint.
"""
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, Dict, List, Any, Union


class CheckoutSessionRequest(BaseModel):
    """Request model for creating a checkout session."""
    price_id: Optional[str] = Field(
        None,
        description="Stripe Price ID for the product or subscription"
    )
    success_url: HttpUrl = Field(
        ...,
        description="URL to redirect to after successful payment"
    )
    cancel_url: HttpUrl = Field(
        ...,
        description="URL to redirect to if payment is cancelled"
    )
    customer_email: Optional[str] = Field(
        None,
        description="Customer email for prefilling checkout form"
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description="Additional metadata to include with the session"
    )
    mode: str = Field(
        "payment",
        description="Payment mode (subscription, payment, or setup)"
    )
    line_items: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Custom line items for the checkout session"
    )

    @validator("mode")
    def validate_mode(cls, v):
        """Validate that the mode is one of the allowed values."""
        allowed_modes = ["payment", "subscription", "setup"]
        if v not in allowed_modes:
            raise ValueError(f"Mode must be one of: {', '.join(allowed_modes)}")
        return v

    @validator("price_id", "line_items")
    def validate_price_or_line_items(cls, v, values):
        """Validate that either price_id or line_items is provided."""
        if "price_id" in values and values["price_id"] is None and v is None:
            if "line_items" not in values or values["line_items"] is None:
                raise ValueError("Either price_id or line_items must be provided")
        return v


class CheckoutSessionResponse(BaseModel):
    """Response model for the checkout session creation."""
    session_id: str = Field(..., description="Stripe Checkout Session ID")
    url: HttpUrl = Field(..., description="URL to the Stripe Checkout page")