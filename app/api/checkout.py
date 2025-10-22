"""Stripe checkout endpoint implementation."""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
import os
from typing import Optional
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["checkout"])

# Set Stripe API key from environment
# In production, this should come from a proper config/env system
stripe.api_key = os.environ.get("STRIPE_API_KEY")
if not stripe.api_key:
    logger.warning("STRIPE_API_KEY environment variable not set. Checkout will not function correctly.")


class CheckoutRequest(BaseModel):
    """Checkout session request model."""
    price_id: str
    quantity: int = 1
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None
    metadata: Optional[dict] = None


class CheckoutResponse(BaseModel):
    """Checkout session response model."""
    checkout_url: str
    session_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest):
    """
    Create a Stripe checkout session and return the session URL.

    Args:
        request: The checkout request containing price_id, success_url, cancel_url, etc.

    Returns:
        JSON response with the checkout URL

    Raises:
        HTTPException: If there is an error creating the checkout session
    """
    try:
        # Validate Stripe API key
        if not stripe.api_key:
            raise HTTPException(
                status_code=500,
                detail="Stripe API key not configured. Please set the STRIPE_API_KEY environment variable."
            )

        # Create line items for the checkout session
        line_items = [{
            'price': request.price_id,
            'quantity': request.quantity,
        }]

        # Set up additional parameters
        checkout_params = {
            'line_items': line_items,
            'mode': 'payment',  # 'subscription' for subscriptions, 'payment' for one-time
            'success_url': request.success_url,
            'cancel_url': request.cancel_url,
        }

        # Add customer email if provided
        if request.customer_email:
            checkout_params['customer_email'] = request.customer_email

        # Add metadata if provided
        if request.metadata:
            checkout_params['metadata'] = request.metadata

        # Create the checkout session
        session = stripe.checkout.Session.create(**checkout_params)

        # Return the session URL
        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id
        )

    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    except Exception as e:
        # Handle general errors
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating checkout session: {str(e)}")