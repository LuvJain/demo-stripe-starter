"""API routes package - ready for checkout and webhook endpoints"""

from fastapi import APIRouter
from app.api.checkout import router as checkout_router

# Main API router
api_router = APIRouter()

# Include all router modules
api_router.include_router(checkout_router)
