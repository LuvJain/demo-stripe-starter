# Stripe Integration Starter

Minimal FastAPI application ready for Stripe payment integration.

## Structure

```
app/
├── main.py          # Basic FastAPI app
├── api/             # Empty - ready for checkout.py and webhooks.py
├── services/        # Empty - ready for stripe_service.py
└── models/
    └── user.py      # Basic User model (no subscription fields yet)
```

## What's Missing (To Be Implemented)

- `stripe` Python package
- `app/api/checkout.py` - Checkout endpoint
- `app/api/webhooks.py` - Webhook handler
- `app/services/stripe_service.py` - Stripe integration logic
- Subscription fields in User model (subscription_status, subscription_tier, stripe_customer_id)

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit: http://localhost:8000
