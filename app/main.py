"""Main FastAPI application"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, get_session

app = FastAPI(title="Stripe Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Initialize database on application startup"""
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Stripe Integration API - Ready for checkout implementation"}


@app.get("/health")
def health():
    return {"status": "healthy"}
