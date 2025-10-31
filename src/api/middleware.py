"""FastAPI middleware configuration."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import uuid

from src.utils.logging import get_logger

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application.
    
    Args:
        app: FastAPI application instance
    """
    # CORS
    from config.settings import get_settings
    settings = get_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging and timing
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests with timing and request ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s",
            extra={"request_id": request_id, "status_code": response.status_code}
        )
        
        return response

