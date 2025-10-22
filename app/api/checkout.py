"""Stripe checkout session endpoint for handling payment processing"""
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Stripe API key from environment variable
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable not set")

# Create router
router = APIRouter(prefix="/api", tags=["checkout"])


class CheckoutRequest(BaseModel):
    """Request model for creating a checkout session"""
    price_id: str = Field(..., description="Stripe Price ID for the product")
    quantity: int = Field(1, description="Quantity of the item", ge=1)
    success_url: str = Field(
        ...,
        description="URL to redirect to on successful payment"
    )
    cancel_url: str = Field(
        ...,
        description="URL to redirect to on cancelled payment"
    )
    customer_email: str = Field(
        None,
        description="Pre-fill customer email (optional)"
    )


class CheckoutResponse(BaseModel):
    """Response model for checkout session"""
    url: str = Field(..., description="Checkout session URL")
    session_id: str = Field(..., description="Stripe session ID")


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: Request,
    checkout_data: CheckoutRequest
) -> Dict[str, Any]:
    """
    Create a Stripe checkout session and return the session URL

    This endpoint:
    1. Validates the checkout request data
    2. Creates a Stripe checkout session with the provided details
    3. Returns the session URL for redirecting the customer

    The client should redirect the customer to the returned URL to complete payment
    """
    try:
        # Create line items from the request
        line_items = [
            {
                "price": checkout_data.price_id,
                "quantity": checkout_data.quantity,
            }
        ]

        # Set up the checkout session parameters
        session_params = {
            "line_items": line_items,
            "mode": "payment",  # 'subscription' or 'payment'
            "success_url": checkout_data.success_url,
            "cancel_url": checkout_data.cancel_url,
        }

        # Add customer email if provided
        if checkout_data.customer_email:
            session_params["customer_email"] = checkout_data.customer_email

        # Create the checkout session
        session = stripe.checkout.Session.create(**session_params)

        # Return the session URL
        return {
            "url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        # Handle general errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )