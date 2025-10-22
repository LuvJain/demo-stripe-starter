"""Configuration settings for the application."""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Stripe API configuration
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRODUCT_ID = os.getenv("STRIPE_PRODUCT_ID", "")

# Application configuration
APP_URL = os.getenv("APP_URL", "http://localhost:3000")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Success and cancel URLs for Stripe Checkout
CHECKOUT_SUCCESS_URL = f"{APP_URL}/checkout/success"
CHECKOUT_CANCEL_URL = f"{APP_URL}/checkout/cancel"

def get_stripe_config() -> Dict[str, Any]:
    """Return Stripe configuration as a dictionary."""
    return {
        "api_key": STRIPE_API_KEY,
        "webhook_secret": STRIPE_WEBHOOK_SECRET,
        "product_id": STRIPE_PRODUCT_ID,
        "success_url": CHECKOUT_SUCCESS_URL,
        "cancel_url": CHECKOUT_CANCEL_URL,
    }