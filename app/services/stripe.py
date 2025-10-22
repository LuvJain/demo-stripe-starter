"""Stripe service for handling payments and subscriptions"""
import os
from typing import Dict, Any, Optional, List
import stripe
from pydantic import BaseModel, HttpUrl, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe with the API key
stripe.api_key = os.getenv("STRIPE_API_KEY", "")

# If no API key is set, warn but don't crash as we're in development
if not stripe.api_key:
    print("WARNING: STRIPE_API_KEY is not set. Stripe functionality will not work correctly.")
    print("Set this in your environment variables or .env file.")


class StripeCheckoutSessionRequest(BaseModel):
    """Request model for creating a checkout session"""
    price_id: str = Field(..., description="Stripe Price ID to charge")
    success_url: HttpUrl = Field(..., description="URL to redirect on successful payment")
    cancel_url: HttpUrl = Field(..., description="URL to redirect on cancelled payment")
    customer_email: Optional[str] = Field(None, description="Pre-fill customer email if available")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata to associate with the checkout session")


class StripeCheckoutSession(BaseModel):
    """Response model with checkout session URL"""
    checkout_url: HttpUrl = Field(..., description="URL for the checkout session")
    session_id: str = Field(..., description="Stripe Session ID")


def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None
) -> StripeCheckoutSession:
    """
    Create a Stripe checkout session

    Args:
        price_id: The Stripe Price ID
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if customer cancels
        customer_email: Optional customer email to prefill
        metadata: Optional metadata to attach to the session

    Returns:
        StripeCheckoutSession with checkout URL and session ID

    Raises:
        stripe.error.StripeError: On Stripe API errors
    """
    session_params: Dict[str, Any] = {
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        "mode": "subscription",
        "success_url": success_url,
        "cancel_url": cancel_url,
    }

    # Add optional parameters if provided
    if customer_email:
        session_params["customer_email"] = customer_email

    if metadata:
        session_params["metadata"] = metadata

    # Create the checkout session
    session = stripe.checkout.Session.create(**session_params)

    # Return the session URL and ID
    return StripeCheckoutSession(
        checkout_url=session.url,
        session_id=session.id
    )