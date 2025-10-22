"""Stripe checkout endpoint
This module handles the creation of Stripe checkout sessions.
"""
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe API key
stripe.api_key = os.getenv("STRIPE_API_KEY")
if not stripe.api_key:
    raise ValueError("Missing STRIPE_API_KEY environment variable")

# Create router
router = APIRouter(
    prefix="/api",
    tags=["checkout"],
    responses={404: {"description": "Not found"}},
)

# Models for request and response
class CheckoutRequest(BaseModel):
    """Request model for checkout session creation"""
    price_id: str = Field(..., description="Stripe Price ID for the product")
    quantity: int = Field(1, description="Quantity of the product", ge=1)
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect after cancelled payment")

class CheckoutResponse(BaseModel):
    """Response model for checkout session creation"""
    session_url: str = Field(..., description="URL to the Stripe checkout session")
    session_id: str = Field(..., description="Stripe Session ID")

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest) -> Dict[str, Any]:
    """Create a Stripe checkout session

    Args:
        request: Checkout request data with price_id and redirect URLs

    Returns:
        Dictionary containing the checkout session URL

    Raises:
        HTTPException: If session creation fails
    """
    try:
        # Create line items from request
        line_items = [
            {
                "price": request.price_id,
                "quantity": request.quantity,
            }
        ]

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )

        # Return session URL
        return {
            "session_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )