"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router from the API package
from app.api.checkout import router as checkout_router

app = FastAPI(title="Stripe Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the checkout router
app.include_router(checkout_router)


@app.get("/")
def root():
    return {"message": "Stripe Integration API - Checkout implementation complete"}


@app.get("/health")
def health():
    return {"status": "healthy"}
