"""Checkout API endpoints for Stripe integration."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.services.stripe import StripeService

router = APIRouter(prefix="/api", tags=["checkout"])


class CheckoutRequest(BaseModel):
    """
    Request model for creating a checkout session.
    """
    price_id: str = Field(..., description="Stripe Price ID to use for checkout")
    quantity: int = Field(1, description="Quantity of items to purchase", ge=1)
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description="Optional metadata to include with the checkout session"
    )


class CheckoutResponse(BaseModel):
    """
    Response model for the checkout session.
    """
    session_id: str
    url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest
) -> Dict[str, Any]:
    """
    Create a Stripe checkout session and return the session URL.

    Args:
        request: The checkout request containing price_id, quantity, and optional metadata.

    Returns:
        Dictionary containing the Stripe session ID and checkout URL.

    Raises:
        HTTPException: If there's an error creating the checkout session.
    """
    try:
        # Create the checkout session using the Stripe service
        result = await StripeService.create_checkout_session(
            price_id=request.price_id,
            quantity=request.quantity,
            metadata=request.metadata
        )

        return result
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))