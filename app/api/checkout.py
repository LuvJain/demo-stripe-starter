"""
Stripe checkout endpoint implementation
"""
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import stripe

# Initialize Stripe with API key from environment variable
stripe.api_key = os.environ.get("STRIPE_API_KEY")

# Create router for checkout endpoints
router = APIRouter(prefix="/api", tags=["checkout"])


class CheckoutRequest(BaseModel):
    """Request model for checkout session creation"""
    price_id: str
    quantity: int = 1
    success_url: HttpUrl
    cancel_url: HttpUrl


class CheckoutResponse(BaseModel):
    """Response model with checkout session URL"""
    checkout_url: HttpUrl
    session_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session for payment processing

    Args:
        request: Checkout request containing price ID, quantity, and redirect URLs

    Returns:
        Dictionary with checkout session URL and session ID

    Raises:
        HTTPException: If there's an error creating the checkout session
    """
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": request.price_id,
                    "quantity": request.quantity,
                }
            ],
            mode="subscription",
            success_url=str(request.success_url),
            cancel_url=str(request.cancel_url),
        )

        # Return checkout URL and session ID
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e)) from e