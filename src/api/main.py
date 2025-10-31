"""FastAPI main application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config.settings import get_settings
from src.api.middleware import setup_middleware
from src.api.v1.routes import health, tts, emotions
from src.api.dependencies import get_speech_service
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Emotional Speech Generation API...")
    settings = get_settings()
    
    # Initialize and load TTS model
    try:
        speech_service = get_speech_service()
        speech_service.tts_engine.load_model()
        logger.info(f"TTS model loaded successfully: {settings.model_name}")
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        # Continue anyway - will fail gracefully on synthesis requests
    
    yield
    
    # Shutdown
    logger.info("Shutting down Emotional Speech Generation API...")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready emotional text-to-speech API for documentary narration",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(tts.router, prefix=settings.api_v1_prefix)
app.include_router(emotions.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

