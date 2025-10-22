"""Stripe service for webhook handling and payment operations"""
import json
import stripe
import os
from fastapi import HTTPException, Request
from sqlmodel import Session, select
from datetime import datetime
from typing import Dict, Any, Optional

from app.models import Order, PaymentStatus


# Load Stripe API key from environment variables
# In a real app, this would come from a .env file loaded by python-dotenv
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "sk_test_your_key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_your_signing_secret")

# Initialize Stripe
stripe.api_key = STRIPE_API_KEY


class StripeService:
    """Service for Stripe-related operations"""

    @staticmethod
    async def verify_webhook_signature(request: Request, signature: str) -> Dict[str, Any]:
        """
        Verify the Stripe webhook signature and return the event

        Args:
            request: The FastAPI request object
            signature: The Stripe signature from the headers

        Returns:
            The verified Stripe event

        Raises:
            HTTPException: If signature verification fails
        """
        try:
            # Get the request body as bytes
            payload = await request.body()

            # Verify the signature
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )

            return event
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            # Other errors
            raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    @staticmethod
    def handle_payment_intent_succeeded(event: Dict[str, Any], db: Session) -> Order:
        """
        Handle the payment_intent.succeeded event

        Args:
            event: The Stripe event
            db: Database session

        Returns:
            The updated order
        """
        # Get the payment intent from the event
        payment_intent = event['data']['object']
        payment_intent_id = payment_intent['id']

        # Find the order with this payment intent
        order_stmt = select(Order).where(Order.payment_intent_id == payment_intent_id)
        order = db.exec(order_stmt).first()

        if not order:
            # No matching order found - log this in a real application
            # This might happen if webhooks arrive out of order
            return None

        # Update the order
        order.payment_status = PaymentStatus.SUCCEEDED
        order.updated_at = datetime.utcnow()

        # Save to database
        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def handle_payment_intent_failed(event: Dict[str, Any], db: Session) -> Optional[Order]:
        """
        Handle the payment_intent.failed event

        Args:
            event: The Stripe event
            db: Database session

        Returns:
            The updated order or None if not found
        """
        # Get the payment intent from the event
        payment_intent = event['data']['object']
        payment_intent_id = payment_intent['id']

        # Find the order with this payment intent
        order_stmt = select(Order).where(Order.payment_intent_id == payment_intent_id)
        order = db.exec(order_stmt).first()

        if not order:
            # No matching order found
            return None

        # Update the order
        order.payment_status = PaymentStatus.FAILED
        order.updated_at = datetime.utcnow()

        # Optionally store failure reason from payment_intent
        if payment_intent.get('last_payment_error'):
            error_message = payment_intent['last_payment_error'].get('message', 'Unknown error')
            # In a real app, you might store this in order.metadata or a dedicated field

        # Save to database
        db.add(order)
        db.commit()
        db.refresh(order)

        return order