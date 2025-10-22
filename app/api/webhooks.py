"""Stripe webhook handler for processing payment events"""
import os
import json
import stripe
import logging
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Order, PaymentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Create router
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    """
    Handle Stripe webhook events

    This endpoint processes webhook events from Stripe, specifically focusing on
    payment_intent.succeeded and payment_intent.failed events to update order status.

    The endpoint validates the webhook signature using the STRIPE_WEBHOOK_SECRET
    environment variable.
    """
    # Get the raw request payload
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    # Validate webhook signature
    try:
        # Verify the event came from Stripe using the webhook secret
        if not webhook_secret:
            logger.warning("No Stripe webhook secret found in environment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook secret not configured",
            )

        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Extract event type
    event_type = event.get("type")
    logger.info(f"Received Stripe webhook event: {event_type}")

    # Handle specific event types
    if event_type == "payment_intent.succeeded":
        await handle_payment_intent_succeeded(event.data.object, session)
    elif event_type == "payment_intent.failed":
        await handle_payment_intent_failed(event.data.object, session)
    else:
        logger.info(f"Unhandled event type: {event_type}")

    # Return a 200 response to Stripe
    return Response(status_code=status.HTTP_200_OK)


async def handle_payment_intent_succeeded(payment_intent, session: Session):
    """
    Handle payment_intent.succeeded event

    Updates the corresponding order in the database to 'succeeded' status
    """
    payment_intent_id = payment_intent.get("id")
    logger.info(f"Processing successful payment: {payment_intent_id}")

    # Find order by payment intent ID
    order = find_order_by_payment_intent(payment_intent_id, session)
    if order:
        # Update order status
        order.payment_status = PaymentStatus.SUCCEEDED
        session.add(order)
        session.commit()
        logger.info(f"Order {order.id} updated to status: {order.payment_status}")
    else:
        logger.warning(f"Order not found for payment intent: {payment_intent_id}")


async def handle_payment_intent_failed(payment_intent, session: Session):
    """
    Handle payment_intent.failed event

    Updates the corresponding order in the database to 'failed' status
    """
    payment_intent_id = payment_intent.get("id")
    logger.info(f"Processing failed payment: {payment_intent_id}")

    # Find order by payment intent ID
    order = find_order_by_payment_intent(payment_intent_id, session)
    if order:
        # Update order status
        order.payment_status = PaymentStatus.FAILED
        session.add(order)
        session.commit()
        logger.info(f"Order {order.id} updated to status: {order.payment_status}")
    else:
        logger.warning(f"Order not found for payment intent: {payment_intent_id}")


def find_order_by_payment_intent(payment_intent_id: str, session: Session) -> Order:
    """
    Find an order by its Stripe payment intent ID

    Args:
        payment_intent_id: Stripe payment intent ID
        session: Database session

    Returns:
        Order object if found, None otherwise
    """
    statement = select(Order).where(Order.stripe_payment_intent_id == payment_intent_id)
    return session.exec(statement).first()