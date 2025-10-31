"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime

from config.settings import get_settings
from src.api.dependencies import get_speech_service

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether TTS model is loaded")
    timestamp: datetime = Field(..., description="Current server time")


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns service status and basic information.
    """
    settings = get_settings()
    speech_service = get_speech_service()
    model_info = speech_service.get_model_info()
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        model_loaded=model_info.get("loaded", False),
        timestamp=datetime.now()
    )


@router.get("/ready", status_code=200)
async def readiness_check() -> dict:
    """
    Readiness check for Kubernetes/deployment systems.
    
    Returns 200 if service is ready to handle requests, 503 otherwise.
    """
    try:
        speech_service = get_speech_service()
        model_info = speech_service.get_model_info()
        
        if not model_info.get("loaded", False):
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        return {"status": "ready"}
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

