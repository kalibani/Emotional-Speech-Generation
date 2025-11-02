# Emotional Speech Generation 🎙️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

**Emotional text-to-speech system for documentary-style narration.**

---

## 🌟 Features

- ✅ **6 Emotional Styles**: neutral, excited, sad, serious, empathetic, urgent
- ✅ **Intensity Control**: Fine-tune emotion strength (0.0-1.0)
- ✅ **Production-Ready API**: FastAPI with OpenAPI docs
- ✅ **CLI Tool**: Simple command-line interface
- ✅ **High-Quality Output**: 24kHz audio with professional processing
- ✅ **Docker Support**: Easy deployment with Docker/Docker Compose
- ✅ **Comprehensive Tests**: Unit, integration, and API tests
- ✅ **Type-Safe**: Full type hints and Pydantic validation

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### **Option 1: CLI** - Recommended

```bash
# 1. Create virtual environment (recommended to avoid conflicts)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate speech! (models download automatically on first run)
python scripts/solution.py "Hello world" output.wav

# With emotion
python scripts/solution.py "This is amazing!" output.wav --emotion excited --intensity 0.8
```

### **Option 2: API**

```bash
# Setup
make install
make setup

# Run API server
make run

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### **Option 3: Docker**

```bash
# Build and run
docker-compose up

# API available at http://localhost:8000
```

---

## 📦 Installation

### **Requirements**

- Python 3.9+
- 4GB+ RAM (8GB recommended)
- Optional: CUDA-compatible GPU for faster synthesis

### **Step 1: Clone Repository**

```bash
git clone https://github.com/yourusername/emotional-speech-generation.git
cd emotional-speech-generation
```

### **Step 2: Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
# Install all dependencies
pip install -r requirements.txt

```

### **Step 4: Run the CLI**

```bash
# Generate speech (models download automatically on first run)
python scripts/solution.py "Hello world" output.wav

# Models will be downloaded to ~/.cache/ on first use
# Subsequent runs will be faster
```

---

## 💻 Usage

### **CLI Usage**

#### **Basic Synthesis**

```bash
python scripts/solution.py "Hello world" output.wav
```

#### **With Emotions**

```bash
# Excited narration
python scripts/solution.py "An incredible discovery!" output.wav --emotion excited --intensity 0.8

# Somber tone
python scripts/solution.py "Unfortunately, this happened." output.wav --emotion sad --intensity 0.6

# Serious narration
python scripts/solution.py "This is critical information." output.wav --emotion serious --intensity 0.7
```

#### **Advanced Options**

```bash
# From file
python scripts/solution.py --input script.txt output.wav --emotion excited

# Custom settings
python scripts/solution.py "Hello" output.wav \
  --emotion excited \
  --intensity 0.8 \
  --sample-rate 44100 \
  --remove-silence \
  --speed 1.1

# List available emotions
python scripts/solution.py --list-emotions
```

### **API Usage**

#### **Start Server**

```bash
# Development mode
uvicorn src.api.main:app --reload

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### **Example Requests**

```bash
# Health check
curl http://localhost:8000/v1/health

# List emotions
curl http://localhost:8000/v1/emotions

# Synthesize speech
curl -X POST http://localhost:8000/v1/speech/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to this fascinating documentary.",
    "emotion": "excited",
    "intensity": 0.7
  }'

# Download audio
curl http://localhost:8000/audio/<job_id>.wav --output narration.wav
```

---

## 📚 API Documentation

### **Endpoints**

| Method | Endpoint                | Description         |
| ------ | ----------------------- | ------------------- |
| `GET`  | `/v1/health`            | Health check        |
| `GET`  | `/v1/health/ready`      | Readiness check     |
| `GET`  | `/v1/emotions`          | List all emotions   |
| `GET`  | `/v1/emotions/{id}`     | Get emotion details |
| `POST` | `/v1/speech/synthesize` | Generate speech     |
| `GET`  | `/audio/{filename}`     | Download audio file |

### **Interactive Documentation**

Once the API is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Example: Synthesize Speech**

**Request:**

```json
POST /v1/speech/synthesize

{
  "text": "Welcome to our documentary about the cosmos.",
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
  "audio_url": "/audio/123e4567-e89b-12d3-a456-426614174000.wav",
  "duration_seconds": 8.3,
  "metadata": {
    "text_length": 45,
    "emotion_applied": "excited",
    "intensity": 0.7,
    "processing_time_ms": 1247,
    "model": "chatterbox"
  },
  "expires_at": "2025-10-31T12:00:00Z"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Health     │  │     TTS      │  │   Emotions   │      │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           │                                 │
│                  ┌────────┴────────┐                       │
│                  │ Speech Service  │                       │
│                  └────────┬────────┘                       │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐             │
│         │                 │                 │             │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐      │
│  │    Text     │  │     TTS     │  │    Audio    │      │
│  │  Processor  │  │   Engine    │  │  Processor  │      │
│  └─────────────┘  └──────┬──────┘  └─────────────┘      │
│                           │                               │
│                  ┌────────┴────────┐                     │
│                  │  Chatterbox TTS      │                     │
│                  │  Model          │                     │
│                  └─────────────────┘                     │
└───────────────────────────────────────────────────────────┘
```

### **Project Structure**

```
emotional-speech-generation/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── v1/
│   │   │   ├── routes/   # API endpoints
│   │   │   └── schemas/  # Pydantic models
│   │   ├── main.py
│   │   └── middleware.py
│   ├── core/             # Business logic
│   │   ├── tts_engine.py
│   │   ├── emotion_controller.py
│   │   ├── text_processor.py
│   │   └── audio_processor.py
│   ├── models/           # TTS model implementations
│   ├── services/         # High-level services
│   └── utils/            # Utilities
├── config/               # Configuration files
├── scripts/              # CLI and setup scripts
│   └── solution.py       # Solution
├── tests/                # Test suite
├── docs/                 # Documentation
└── data/                 # Models and audio cache
```

For detailed architecture documentation, see [Architecture Guide](docs/architecture.md).

---

## ⚙️ Configuration

Configuration is managed through environment variables and `.env` file.

### **Environment Variables**

```bash
# Application
APP_NAME="Emotional Speech Generation API"
DEBUG=false

# TTS Model
MODEL_NAME=chatterbox          # coqui, chatterbox, bark
DEVICE=cpu                # cpu, cuda, mps
MODEL_CACHE_DIR=data/models

# Audio Settings
DEFAULT_SAMPLE_RATE=24000
MAX_TEXT_LENGTH=5000

# API
CORS_ORIGINS=["*"]
RATE_LIMIT_REQUESTS=10
```

Copy `.env.example` to `.env` and customize.

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-unit          # Unit tests only
make test-api           # API tests only

# With coverage report
pytest --cov=src --cov-report=html

# View coverage
open htmlcov/index.html
```

### **Test Coverage**

Current coverage: **85%+**

- ✅ Unit tests: Text processing, emotion control, audio processing
- ✅ Integration tests: TTS engine, speech service
- ✅ API tests: All endpoints, error handling

---

## 🚀 Deployment

### **Docker Deployment**

```bash
# Build image
docker build -t emotional-tts:latest .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data emotional-tts:latest

# Or use docker-compose
docker-compose up -d
```

### **Production Deployment**

```bash
# With Gunicorn + Uvicorn workers
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120

# With systemd service
sudo cp deployment/emotional-tts.service /etc/systemd/system/
sudo systemctl enable emotional-tts
sudo systemctl start emotional-tts
```

For detailed deployment guide, see [Deployment Documentation](docs/deployment.md).

---

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Stuck in Quote Prompt (`dquote>`)**

**Problem:** Terminal shows `dquote>` and waits for input

```bash
python scripts/solution.py "This is amazing!" output.wav
dquote>
```

**Cause:** You're using **smart quotes** `"` `"` (curly quotes) instead of **straight quotes** `" "`

**Solution:**

- Press `Ctrl + C` to exit
- **Type the command manually** using the quote key on your keyboard (don't copy/paste from formatted documents)
- OR copy from terminal/plain text editor only

```bash
# ✅ CORRECT (straight quotes)
python scripts/solution.py "Hello world" output.wav

# ❌ WRONG (smart/curly quotes from Word/Pages/websites)
python scripts/solution.py "Hello world" output.wav
```

---

#### **2. Protobuf Version Error**

**Problem:** `AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'`

**Solution:**

```bash
# Downgrade protobuf
pip install "protobuf<5.0,>=3.20.3"

# OR better: use clean virtual environment
python3 -m venv venv-clean
source venv-clean/bin/activate
pip install -r requirements.txt
```

---

#### **3. Module Not Found Errors**

**Problem:** `ModuleNotFoundError: No module named 'chatterbox'`

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### **4. Dependency Conflicts**

**Problem:** Seeing many dependency warnings during installation

**Cause:** Other packages installed globally (tensorflow, facenet, etc.)

**Solution:** Use a **clean virtual environment** (recommended):

```bash
# Create isolated environment
python3 -m venv venv-tts
source venv-tts/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Dependency warnings for packages our project doesn't use (like tensorflow) won't affect functionality.

---

## 🎯 CLI

The CLI (`scripts/solution.py`) requirements:

✅ **Required Functionality:**

- Input: text string
- Output: `.wav` file with synthesized speech
- Runnable via: `python scripts/solution.py "Hello world" hello.wav`

✅ **Bonus Features:**

- ✅ Support for 6 different emotional styles
- ✅ Intensity control for fine-tuning
- ✅ Comprehensive error handling
- ✅ Invalid input gracefully handled
- ✅ Help documentation (`--help`)
- ✅ Progress indicators

### **Why Chatterbox (Primary) with Coqui Fallback?**

**Primary: Chatterbox**

- **Best Quality**: Outperformed ElevenLabs in blind tests (63.8% preference)
- **True Emotion Control**: Built-in emotion intensity via exaggeration parameter
- **Open-source**: MIT licensed, production-ready
- **Multi-device**: Works on CUDA (NVIDIA), MPS (Apple Silicon), and CPU

**Fallback: Coqui TTS**

- **Reliability**: Mature ecosystem, extensive documentation
- **Lightweight**: Smaller model size, faster download
- **Wide compatibility**: Works in all environments

**Switching Models:**

```bash
# Use Chatterbox (default)
python scripts/solution.py "text" output.wav

# Use Coqui fallback
export MODEL_NAME=coqui
python scripts/solution.py "text" output.wav

# Or in .env file
echo "MODEL_NAME=coqui" >> .env
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Setup**

```bash
# Install dev dependencies
make install-dev

# Run linters
make lint

# Format code
make format

# Run tests
make test
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Chatterbox TTS** for the excellent open-source TTS framework
- **FastAPI** for the modern web framework
- **The open-source community** for making this possible

---

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

Made with ❤️ by [Kautzar Alibani](mailto:kalibani.ka@gmail.com) for documentary narration
