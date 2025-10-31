"""TTS synthesis endpoints."""

import time
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse

from src.api.v1.schemas.tts import SynthesizeRequest, SynthesizeResponse, SynthesisMetadata
from src.api.v1.schemas.errors import ErrorResponse
from src.services.speech_service import SpeechService
from src.api.dependencies import get_speech_service, rate_limit
from src.utils.logging import get_logger

router = APIRouter(prefix="/speech", tags=["speech"])
logger = get_logger(__name__)


@router.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def synthesize_speech(
    request: SynthesizeRequest,
    speech_service: SpeechService = Depends(get_speech_service),
    _: None = Depends(rate_limit)
) -> SynthesizeResponse:
    """
    Synthesize emotional speech from text.
    
    This endpoint generates speech audio with the specified emotion and intensity.
    The audio is saved to the server and a URL is returned for download.
    
    **Request Body:**
    - **text**: Input text to synthesize (1-5000 characters)
    - **emotion**: Emotion to apply (neutral, excited, sad, serious, empathetic, urgent)
    - **intensity**: Emotion strength (0.0-1.0, where 0=neutral, 1=full emotion)
    - **voice_id**: Voice preset to use (default: default_documentary)
    - **output_format**: Audio format (wav, mp3, ogg)
    - **sample_rate**: Sample rate in Hz (16000, 22050, 24000, 44100)
    - **options**: Additional processing options
    
    **Response:**
    - **job_id**: Unique identifier for this synthesis job
    - **status**: Synthesis status (completed, processing, failed)
    - **audio_url**: URL to download the generated audio
    - **duration_seconds**: Length of the generated audio
    - **metadata**: Processing details and metadata
    - **expires_at**: When the audio URL will expire
    """
    try:
        start_time = time.time()
        
        # Convert Pydantic model to dict
        options = request.options.model_dump() if request.options else None
        
        # Synthesize speech
        result = await speech_service.synthesize(
            text=request.text,
            emotion=request.emotion,
            intensity=request.intensity,
            voice_id=request.voice_id,
            output_format=request.output_format,
            sample_rate=request.sample_rate,
            options=options
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return SynthesizeResponse(
            job_id=result.job_id,
            status="completed",
            audio_url=result.audio_url,
            duration_seconds=result.duration,
            metadata=SynthesisMetadata(
                text_length=len(request.text),
                emotion_applied=request.emotion,
                intensity=request.intensity,
                processing_time_ms=processing_time,
                model=result.model_name
            ),
            expires_at=result.expires_at
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "request_id": "request_id_placeholder"
            }
        )
    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TTS_ENGINE_ERROR",
                "message": "Speech synthesis failed",
                "request_id": "request_id_placeholder"
            }
        )


@router.get("/audio/{filename}")
async def get_audio_file(filename: str) -> FileResponse:
    """
    Download generated audio file.
    
    **Parameters:**
    - **filename**: Name of the audio file to download
    
    **Returns:**
    The audio file as a downloadable response.
    """
    from pathlib import Path
    from config.settings import get_settings
    
    settings = get_settings()
    file_path = Path(settings.audio_output_dir) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Determine media type based on extension
    media_type_map = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg"
    }
    media_type = media_type_map.get(file_path.suffix, "application/octet-stream")
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename
    )

