"""Stripe webhook handling endpoints"""
import json
from fastapi import APIRouter, Request, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Dict, Any, Optional

from app.database import get_session
from app.services.stripe_service import StripeService

# Create router
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_session)
) -> JSONResponse:
    """
    Handle Stripe webhook events

    This endpoint handles Stripe webhook events, specifically:
    - payment_intent.succeeded
    - payment_intent.failed

    Args:
        request: The FastAPI request object
        stripe_signature: The Stripe-Signature header
        db: Database session dependency

    Returns:
        JSONResponse with processing status
    """
    try:
        # Verify the webhook signature
        event = await StripeService.verify_webhook_signature(request, stripe_signature)

        # Process different event types
        event_type = event.get('type')
        result = {"status": "received", "event_type": event_type}

        # Handle payment_intent.succeeded
        if event_type == 'payment_intent.succeeded':
            order = StripeService.handle_payment_intent_succeeded(event, db)
            if order:
                result["order_id"] = order.id
                result["payment_status"] = order.payment_status
                result["message"] = "Payment succeeded, order updated"
            else:
                result["message"] = "Payment succeeded, but no matching order found"

        # Handle payment_intent.failed
        elif event_type == 'payment_intent.failed':
            order = StripeService.handle_payment_intent_failed(event, db)
            if order:
                result["order_id"] = order.id
                result["payment_status"] = order.payment_status
                result["message"] = "Payment failed, order updated"
            else:
                result["message"] = "Payment failed, but no matching order found"

        # Handle other events
        else:
            result["message"] = f"Event {event_type} received but not processed"

        return JSONResponse(content=result)

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log the error in a real application
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error processing webhook: {str(e)}"}
        )