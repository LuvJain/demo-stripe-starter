"""Stripe checkout endpoint"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.services.stripe import (
    StripeCheckoutSessionRequest,
    StripeCheckoutSession,
    create_checkout_session
)

import stripe

# Create router
router = APIRouter(
    prefix="/api",
    tags=["checkout"],
)


@router.post("/checkout", response_model=StripeCheckoutSession)
async def create_stripe_checkout(
    checkout_req: StripeCheckoutSessionRequest
) -> StripeCheckoutSession:
    """
    Create a Stripe checkout session and return the checkout URL

    This endpoint:
    1. Takes the price ID and URLs as input
    2. Creates a Stripe checkout session using the stripe-python SDK
    3. Returns the checkout session URL and ID

    Returns:
        StripeCheckoutSession: Object containing checkout_url and session_id
    """
    try:
        # Create the checkout session
        checkout_session = create_checkout_session(
            price_id=checkout_req.price_id,
            success_url=str(checkout_req.success_url),
            cancel_url=str(checkout_req.cancel_url),
            customer_email=checkout_req.customer_email,
            metadata=checkout_req.metadata
        )

        return checkout_session

    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        error_message = str(e)
        # Log the error
        print(f"Stripe error: {error_message}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {error_message}")

    except Exception as e:
        # Handle any other errors
        error_message = str(e)
        # Log the error
        print(f"Error creating checkout session: {error_message}")
        raise HTTPException(status_code=500, detail="Internal server error")