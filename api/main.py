"""FastAPI application entry point."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI

from .models import HealthResponse
from .routes import router

app = FastAPI(
    title="GitHub Analytics API",
    description="REST API wrapper for GitHub Analytics MCP Server",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse()
