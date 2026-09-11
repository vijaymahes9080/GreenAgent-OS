"""
GreenAgent OS — FastAPI Main Application
AI-Agent Execution Optimization Platform
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.app.config import settings
from backend.app.core.database import init_db
from backend.app.api.telemetry import router as telemetry_router, workloads_router
from backend.app.api.models import router as models_router
from backend.app.api.optimizer import router as optimizer_router
from backend.app.api.scheduler import router as scheduler_router
from backend.app.api.cache import router as cache_router
from backend.app.api.integrations import router as integrations_router
from backend.app.api.benchmarks import router as benchmarks_router

# Initialize SQLite database
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-quality open-source AI-agent execution optimization platform. "
        "Measures and reduces energy, carbon footprint, cost, and redundant computation "
        "of AI workflows while preserving quality, latency, and deadlines."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security & Timing Headers Middleware
@app.middleware("http")
async def add_security_and_timing_headers(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000.0

    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Mount Routers
app.include_router(telemetry_router, prefix=settings.API_PREFIX)
app.include_router(workloads_router, prefix=settings.API_PREFIX)
app.include_router(models_router, prefix=settings.API_PREFIX)
app.include_router(optimizer_router, prefix=settings.API_PREFIX)
app.include_router(scheduler_router, prefix=settings.API_PREFIX)
app.include_router(cache_router, prefix=settings.API_PREFIX)
app.include_router(integrations_router, prefix=settings.API_PREFIX)
app.include_router(benchmarks_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for container probes and uptime monitoring."""
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "inference_engine": "ollama_or_deterministic_sim",
        "gpu_required": False
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Welcome to GreenAgent OS API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }
