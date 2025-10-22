"""Stripe webhook handler to process payment events"""
import stripe
import json
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import Optional
import os

from app.database import get_session
from app.models import Order, PaymentStatus

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# Get Stripe API key and webhook secret from environment variables
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "sk_test_your_key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_your_signing_secret")

# Initialize Stripe
stripe.api_key = STRIPE_API_KEY


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    session: Session = Depends(get_session)
):
    """
    Webhook endpoint for Stripe events

    This endpoint handles payment_intent.succeeded and payment_intent.failed events
    from Stripe and updates the corresponding order in the database
    """
    if not stripe_signature:
        logger.error("Stripe-Signature header missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )

    # Get the raw request body for signature verification
    payload = await request.body()

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET
        )

        # Extract event data
        event_data = event.data.object
        event_type = event.type

        logger.info(f"Processing Stripe event: {event_type}")

        # Handle specific event types
        if event_type == "payment_intent.succeeded":
            await handle_payment_intent_succeeded(session, event_data)

        elif event_type == "payment_intent.failed":
            await handle_payment_intent_failed(session, event_data)

        else:
            # Log unhandled event types for debugging
            logger.info(f"Unhandled event type: {event_type}")

        return {"status": "success"}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def handle_payment_intent_succeeded(session: Session, payment_intent):
    """Handle successful payment intent by updating order status"""
    # Get payment_intent ID
    payment_intent_id = payment_intent.id

    # Find the order with this payment intent
    statement = select(Order).where(Order.payment_intent_id == payment_intent_id)
    order = session.exec(statement).first()

    if not order:
        logger.warning(f"Order not found for payment_intent_id: {payment_intent_id}")
        return

    # Update the order status
    order.update_status(PaymentStatus.SUCCEEDED)
    session.add(order)
    session.commit()

    logger.info(f"Order {order.id} payment succeeded (payment_intent: {payment_intent_id})")


async def handle_payment_intent_failed(session: Session, payment_intent):
    """Handle failed payment intent by updating order status"""
    # Get payment_intent ID
    payment_intent_id = payment_intent.id

    # Find the order with this payment intent
    statement = select(Order).where(Order.payment_intent_id == payment_intent_id)
    order = session.exec(statement).first()

    if not order:
        logger.warning(f"Order not found for payment_intent_id: {payment_intent_id}")
        return

    # Update the order status
    order.update_status(PaymentStatus.FAILED)
    session.add(order)
    session.commit()

    logger.info(f"Order {order.id} payment failed (payment_intent: {payment_intent_id})")