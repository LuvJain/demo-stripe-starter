"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import API router
from app.api import api_router

# Load environment variables
if os.getenv("STRIPE_API_KEY") is None:
    print("Warning: STRIPE_API_KEY environment variable not set")

# Create FastAPI app
app = FastAPI(title="Stripe Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Stripe Integration API - Checkout endpoint implemented"}


@app.get("/health")
def health():
    return {"status": "healthy"}
