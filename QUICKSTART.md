# Quick Reference Guide

## 🚀 Fastest Way to Get Started

### For Part B (CLI Solution)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup (downloads models, ~500MB)
python scripts/setup_models.py

# 3. Generate speech!
python scripts/solution.py "Hello world" output.wav

# With emotion
python scripts/solution.py "This is amazing!" output.wav --emotion excited --intensity 0.8
```

---

## 📋 Common Commands

### CLI Usage

```bash
# Basic
python scripts/solution.py "Your text here" output.wav

# List emotions
python scripts/solution.py --list-emotions

# From file
python scripts/solution.py --input script.txt output.wav --emotion excited

# Advanced options
python scripts/solution.py "text" output.wav \
  --emotion serious \
  --intensity 0.7 \
  --sample-rate 44100 \
  --remove-silence \
  --speed 1.1
```

### API Usage

```bash
# Start API
make run
# OR
uvicorn src.api.main:app --reload

# Health check
curl http://localhost:8000/v1/health

# List emotions
curl http://localhost:8000/v1/emotions

# Generate speech
curl -X POST http://localhost:8000/v1/speech/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "emotion": "neutral"}'
```

### Development

```bash
# Run tests
make test

# Lint code
make lint

# Format code
make format

# Clean cache
make clean
```

### Docker

```bash
# Build
docker build -t emotional-tts .

# Run
docker run -p 8000:8000 emotional-tts

# With docker-compose
docker-compose up
```

---

## 🎭 Available Emotions

| Emotion | Best For | Example |
|---------|----------|---------|
| `neutral` | Facts, general narration | "The population is 7 billion." |
| `excited` | Discoveries, revelations | "Scientists made a breakthrough!" |
| `sad` | Tragedies, loss | "Unfortunately, they went extinct." |
| `serious` | Important warnings | "This is critical information." |
| `empathetic` | Human stories | "She overcame great challenges." |
| `urgent` | Dramatic events | "Time was running out!" |

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
MODEL_NAME=coqui
DEVICE=cpu                    # cpu, cuda, mps
DEBUG=false
MAX_TEXT_LENGTH=5000
DEFAULT_SAMPLE_RATE=24000
```

### Emotion Settings

Edit `config/emotions.yaml` to customize:
- Prosody parameters (pitch, energy, tempo)
- Recommended intensities
- Use case descriptions

---

## 🐛 Troubleshooting

### "No module named 'TTS'"

```bash
pip install TTS
```

### Model download fails

```bash
# Manual download
python scripts/setup_models.py
```

### Out of memory

```bash
# Use CPU instead of GPU
export DEVICE=cpu

# Or reduce text length
export MAX_TEXT_LENGTH=1000
```

### Audio quality issues

```bash
# Increase sample rate
--sample-rate 44100

# Enable normalization
--no-normalize=false
```

---

## 📖 Quick Links

- **Documentation:** [README.md](README.md)
- **System Design:** [DESIGN.md](DESIGN.md)
- **API Reference:** [docs/api.md](docs/api.md)
- **Deployment:** [docs/deployment.md](docs/deployment.md)
- **API Docs (interactive):** http://localhost:8000/docs

---

## 🎯 Part B Requirements Checklist

- [x] Input: text string ✅
- [x] Output: .wav file ✅
- [x] Runnable via: `python solution.py "text" output.wav` ✅
- [x] Bonus: Multiple styles (6 emotions) ✅
- [x] Bonus: Error handling ✅
- [x] README with setup instructions ✅

---

## 💡 Pro Tips

1. **Test with short text first** to verify setup
2. **Use --list-emotions** to see all options
3. **Start with intensity 0.5** and adjust
4. **Enable --remove-silence** for cleaner audio
5. **Check docs/** for advanced features

---

## 🆘 Need Help?

1. Check error message (they're descriptive!)
2. Run with `--help` flag
3. Read README.md
4. Check logs in `data/logs/`
5. Open an issue on GitHub

---

**Happy narrating!** 🎙️

