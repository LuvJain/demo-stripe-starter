"""Stripe webhook handler for payment events"""
import os
import stripe
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.order import Order, OrderStatus
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# Get Stripe API key and webhook secret from environment
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_your_stripe_test_key")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret")

# Set up Stripe client
stripe.api_key = STRIPE_API_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    """
    Handle Stripe webhook events

    This endpoint receives webhook events from Stripe for payment_intent.succeeded
    and payment_intent.failed events to update order status in the database.
    """
    # Get the raw payload and signature header
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        logger.warning("No Stripe signature header in request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header",
        )

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.warning(f"Invalid Stripe webhook payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.warning(f"Invalid Stripe signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature",
        )

    # Handle the event based on its type
    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Processing Stripe webhook event: {event_type}")

    # Handle specific event types
    if event_type == "payment_intent.succeeded":
        await handle_payment_intent_succeeded(event_data, session)
    elif event_type == "payment_intent.failed":
        await handle_payment_intent_failed(event_data, session)
    else:
        logger.info(f"Unhandled event type: {event_type}")

    return {"status": "success", "event": event_type}


async def handle_payment_intent_succeeded(
    payment_intent: Dict[str, Any], session: Session
) -> None:
    """Handle successful payment intent by updating the order status to paid"""
    payment_intent_id = payment_intent["id"]
    logger.info(f"Payment succeeded for intent ID: {payment_intent_id}")

    # Find the order associated with this payment intent
    order = get_order_by_payment_intent(payment_intent_id, session)

    if order:
        # Update order status to paid
        order.status = OrderStatus.PAID
        session.add(order)
        session.commit()
        logger.info(f"Order {order.id} marked as paid")
    else:
        logger.warning(f"No order found for payment intent ID: {payment_intent_id}")


async def handle_payment_intent_failed(
    payment_intent: Dict[str, Any], session: Session
) -> None:
    """Handle failed payment intent by updating the order status to failed"""
    payment_intent_id = payment_intent["id"]
    logger.info(f"Payment failed for intent ID: {payment_intent_id}")

    # Get error message if available
    error_message = None
    if payment_intent.get("last_payment_error"):
        error_message = payment_intent["last_payment_error"].get("message")

    # Find the order associated with this payment intent
    order = get_order_by_payment_intent(payment_intent_id, session)

    if order:
        # Update order status to failed and store error message
        order.status = OrderStatus.FAILED
        order.error_message = error_message
        session.add(order)
        session.commit()
        logger.info(f"Order {order.id} marked as failed")
    else:
        logger.warning(f"No order found for payment intent ID: {payment_intent_id}")


def get_order_by_payment_intent(payment_intent_id: str, session: Session) -> Optional[Order]:
    """Find an order by its Stripe payment intent ID"""
    query = select(Order).where(Order.stripe_payment_intent_id == payment_intent_id)
    return session.exec(query).first()