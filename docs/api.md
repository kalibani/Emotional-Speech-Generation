# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. In production, use API keys:

```
X-API-Key: your_api_key_here
```

---

## Endpoints

### Health & Status

#### GET /v1/health

Get service health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2025-10-30T12:00:00Z"
}
```

---

### Emotions

#### GET /v1/emotions

List all available emotions.

**Response:**
```json
{
  "emotions": [
    {
      "id": "neutral",
      "name": "Neutral",
      "description": "Standard documentary narration tone",
      "recommended_intensity": 0.5,
      "use_cases": ["facts", "introductions"]
    }
  ]
}
```

---

### Speech Synthesis

#### POST /v1/speech/synthesize

Generate emotional speech from text.

**Request Body:**
```json
{
  "text": "Welcome to this documentary.",
  "emotion": "excited",
  "intensity": 0.7,
  "voice_id": "default_documentary",
  "output_format": "wav",
  "sample_rate": 24000,
  "options": {
    "normalize_audio": true,
    "remove_silence": false,
    "speed": 1.0
  }
}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "audio_url": "/audio/123e4567.wav",
  "duration_seconds": 8.3,
  "metadata": {
    "text_length": 28,
    "emotion_applied": "excited",
    "intensity": 0.7,
    "processing_time_ms": 1247,
    "model": "coqui"
  },
  "expires_at": "2025-10-31T12:00:00Z"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input parameters |
| `INVALID_EMOTION` | Unsupported emotion |
| `TTS_ENGINE_ERROR` | Speech synthesis failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_SERVER_ERROR` | Server error |

---

## Rate Limits

- **Free tier**: 10 requests per minute
- **Paid tier**: 100 requests per minute

---

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/speech/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test.",
    "emotion": "neutral"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/speech/synthesize",
    json={
        "text": "This is amazing!",
        "emotion": "excited",
        "intensity": 0.8
    }
)

data = response.json()
audio_url = data["audio_url"]
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/v1/speech/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello world',
    emotion: 'neutral'
  })
});

const data = await response.json();
console.log(data.audio_url);
```

