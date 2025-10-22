"""
Checkout API endpoints for Stripe integration.
This module contains the endpoint for creating Stripe checkout sessions.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.models.checkout import CheckoutSessionRequest, CheckoutSessionResponse
from app.services.stripe_service import create_checkout_session

# Create router
router = APIRouter(prefix="/api", tags=["checkout"])


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    status_code=200,
    summary="Create a Stripe checkout session",
    description="Creates a new Stripe checkout session and returns the session URL.",
)
async def create_checkout(
    checkout_request: CheckoutSessionRequest,
) -> Dict[str, Any]:
    """
    Create a Stripe checkout session.

    Args:
        checkout_request: The checkout session request data

    Returns:
        A dictionary containing the Stripe session ID and checkout URL

    Raises:
        HTTPException: If there is an error creating the checkout session
    """
    try:
        # Call the stripe service to create a checkout session
        checkout_session = await create_checkout_session(
            price_id=checkout_request.price_id,
            success_url=str(checkout_request.success_url),
            cancel_url=str(checkout_request.cancel_url),
            customer_email=checkout_request.customer_email,
            metadata=checkout_request.metadata,
            mode=checkout_request.mode,
            line_items=checkout_request.line_items,
        )

        return checkout_session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))