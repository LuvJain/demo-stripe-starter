"""
Stripe service for handling Stripe API operations.
This module provides functions for creating checkout sessions and handling webhooks.
"""
import os
import stripe
from fastapi import HTTPException
from typing import Optional, Dict, Any, List

# Initialize Stripe with the API key
stripe.api_key = os.getenv("STRIPE_API_KEY", "")

if not stripe.api_key:
    print("Warning: STRIPE_API_KEY environment variable not set")


async def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    mode: str = "payment",
    line_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session.

    Args:
        price_id: The Stripe Price ID for the product
        success_url: URL to redirect to after successful payment
        cancel_url: URL to redirect to if payment is cancelled
        customer_email: Optional customer email for prefilling
        metadata: Optional metadata to include with the session
        mode: Payment mode (subscription, payment, setup)
        line_items: Optional custom line items (if price_id is not provided)

    Returns:
        Dictionary containing session information including the URL

    Raises:
        HTTPException: If there is an error creating the checkout session
    """
    try:
        # Use provided line items or create one from price_id
        session_line_items = line_items or [{"price": price_id, "quantity": 1}]

        # Prepare session parameters
        session_params = {
            "line_items": session_line_items,
            "mode": mode,
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

        return {
            "session_id": session.id,
            "url": session.url,
        }
    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        raise HTTPException(
            status_code=400,
            detail=f"Error creating checkout session: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )