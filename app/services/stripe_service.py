"""Stripe service for handling API interactions and webhook events"""
import os
import stripe
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, status
from app.models import Order, PaymentStatus
from sqlmodel import Session, select


class StripeService:
    """Service for handling Stripe API interactions and webhook events"""

    def __init__(self):
        """Initialize Stripe with API key from environment variables"""
        stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
        self.webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

        if not stripe.api_key:
            print("Warning: STRIPE_API_KEY environment variable not set")
        if not self.webhook_secret:
            print("Warning: STRIPE_WEBHOOK_SECRET environment variable not set")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> dict:
        """
        Verify Stripe webhook signature and return the event

        Args:
            payload: Raw request body bytes
            signature: Stripe signature from request header

        Returns:
            dict: Verified Stripe event

        Raises:
            HTTPException: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook error: {str(e)}"
            )

    def handle_payment_intent_succeeded(self, event: dict, db: Session) -> Optional[Order]:
        """
        Handle payment_intent.succeeded event

        Args:
            event: Stripe webhook event
            db: Database session

        Returns:
            Optional[Order]: Updated order or None if not found
        """
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        # Find the order with this payment intent
        stmt = select(Order).where(Order.stripe_payment_intent_id == payment_intent_id)
        order = db.exec(stmt).first()

        if not order:
            print(f"Warning: No order found for payment_intent_id: {payment_intent_id}")
            return None

        # Update order status
        order.payment_status = PaymentStatus.SUCCEEDED
        order.updated_at = datetime.utcnow()
        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    def handle_payment_intent_failed(self, event: dict, db: Session) -> Optional[Order]:
        """
        Handle payment_intent.failed event

        Args:
            event: Stripe webhook event
            db: Database session

        Returns:
            Optional[Order]: Updated order or None if not found
        """
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        # Find the order with this payment intent
        stmt = select(Order).where(Order.stripe_payment_intent_id == payment_intent_id)
        order = db.exec(stmt).first()

        if not order:
            print(f"Warning: No order found for payment_intent_id: {payment_intent_id}")
            return None

        # Update order status
        order.payment_status = PaymentStatus.FAILED
        order.updated_at = datetime.utcnow()
        db.add(order)
        db.commit()
        db.refresh(order)

        return order