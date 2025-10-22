"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include API routers
app.include_router(checkout_router)


@app.get("/")
def root():
    return {"message": "Stripe Integration API with checkout endpoint implemented"}


@app.get("/health")
def health():
    return {"status": "healthy"}
