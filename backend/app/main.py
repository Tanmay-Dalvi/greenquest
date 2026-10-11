"""GreenQuest Backend Application Entrypoint."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.routes import router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("greenquest")

app = FastAPI(
    title="GreenQuest API",
    description="Offline-capable outdoor micro-adventure generator for Hacktoberfest 2026",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and Render deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "project": "GreenQuest",
        "description": "Outdoor micro-adventures using open-weight AI",
        "docs": "/docs",
        "health": "/api/health",
    }

