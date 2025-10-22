"""Stripe service for handling payment integration."""
import stripe
from typing import Dict, Any, Optional
from app.config import get_stripe_config

# Initialize Stripe with the API key
stripe_config = get_stripe_config()
stripe.api_key = stripe_config["api_key"]


class StripeService:
    """Service for interacting with the Stripe API."""

    @staticmethod
    async def create_checkout_session(
        price_id: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for a given price ID.

        Args:
            price_id: The Stripe Price ID to use for the checkout.
            quantity: The quantity of items to purchase (default: 1).
            metadata: Additional metadata to attach to the checkout session.

        Returns:
            Dict containing the session ID and URL.
        """
        if not stripe_config["api_key"]:
            raise ValueError("Stripe API key is not configured")

        try:
            # Create line items for the checkout session
            line_items = [
                {
                    "price": price_id,
                    "quantity": quantity,
                }
            ]

            # Default metadata if none provided
            if metadata is None:
                metadata = {}

            # Create the checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=stripe_config["success_url"],
                cancel_url=stripe_config["cancel_url"],
                metadata=metadata
            )

            return {
                "session_id": session.id,
                "url": session.url
            }

        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            error_message = str(e)
            raise Exception(f"Stripe error: {error_message}") from e
        except Exception as e:
            # Handle any other errors
            raise Exception(f"Error creating checkout session: {str(e)}") from e