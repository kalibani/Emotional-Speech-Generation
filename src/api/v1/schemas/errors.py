"""Error response schemas."""

from typing import Optional, Any, List
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    error: str = Field(..., description="Error description")
    value: Optional[Any] = Field(None, description="Invalid value")


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail] | dict] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "INVALID_EMOTION",
                    "message": "Emotion 'super_happy' is not supported.",
                    "details": {
                        "field": "emotion",
                        "value": "super_happy",
                        "allowed_values": ["neutral", "excited", "sad", "serious", "empathetic"]
                    },
                    "request_id": "req-uuid-5678"
                }
            ]
        }
    }

