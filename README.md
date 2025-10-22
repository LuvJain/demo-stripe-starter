# Stripe Integration API

FastAPI application with Stripe payment integration.

## Structure

```
app/
├── main.py          # FastAPI app with routes configured
├── api/             # API endpoints
│   └── checkout.py  # Stripe checkout endpoint
├── services/        # Service layer
│   └── stripe.py    # Stripe integration logic
└── models/
    └── user.py      # Basic User model (no subscription fields yet)
```

## Features Implemented

- Stripe Checkout Session API endpoint
- Stripe service for creating checkout sessions

## What's Missing (To Be Implemented)

- `app/api/webhooks.py` - Webhook handler
- Subscription fields in User model (subscription_status, subscription_tier, stripe_customer_id)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Stripe API key (see `.env.example`):
```
STRIPE_API_KEY=sk_test_your_test_key_here
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000

## Using the Checkout Endpoint

Send a POST request to `/api/checkout` with the following JSON:

```json
{
  "price_id": "price_1234567890",
  "success_url": "https://yourapp.com/success",
  "cancel_url": "https://yourapp.com/cancel",
  "customer_email": "customer@example.com",
  "metadata": {
    "user_id": "123",
    "plan": "premium"
  }
}
```

The response will contain:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

Redirect the user to the `checkout_url` to complete payment.
