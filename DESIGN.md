# System Design Document

## Emotional Speech Generation for Documentary Narration

**Author:** Kautzar Alibani

---

## 1. Pipeline Overview

The system follows a straightforward text-to-speech pipeline with emotion control:

```
Text Input → Text Processing → Emotion Encoding → TTS Model → Vocoder → Post-Processing → Audio Output
```

**Main Steps:**

1. **Text Preprocessing**

   - Normalize numbers ("2024" → "twenty twenty-four")
   - Handle abbreviations and special characters
   - Segment into sentence-level chunks

2. **Emotion Encoding**

   - Map emotion label (excited, sad, neutral, etc.) to model parameters
   - Apply intensity scaling (0.0-1.0)
   - For Chatterbox: maps to `exaggeration` parameter (0.25-2.0)

3. **Speech Synthesis**

   - Feed text + emotion parameters to TTS model
   - Model generates audio with emotional prosody

4. **Post-Processing**
   - Normalize audio levels
   - Remove excessive silence
   - Export as WAV/MP3

---

## 2. Model Selection

### Primary Model: **Chatterbox (Resemble AI)**

After testing several models (spent way too much time on this), Chatterbox turned out to be the sweet spot:

- Beat ElevenLabs in blind tests (63.8% preference) - that's actually impressive
- Has this `exaggeration` parameter (0.25-2.0) that just works - no complex embeddings
- MIT licensed, open source
- Runs on my M1 Mac, NVIDIA GPUs, even CPU
- Can clone voices with 5-10 sec samples

**Why not other models?**

- Tacotron2/FastSpeech2 - no emotion control without heavy fine-tuning
- VITS - good quality but emotion control is painful
- Bark - takes forever to generate, can't control emotions precisely
- StyleTTS2 - more for style transfer than emotions
- ElevenLabs - best quality but costs money + proprietary

### Fallback: **Coqui TTS**

I kept Coqui as backup since Chatterbox is newer and sometimes dependencies break (protobuf issues, fun times). Coqui uses prosody hacks (pitch/tempo tweaks) instead of real emotion control. Less expressive but it always installs.

---

## 3. Emotion Control Strategy

### Approach: Emotion-to-Parameter Mapping

After watching way too many documentaries (Planet Earth, NOVA, Our Planet), I noticed narrators basically use 6 tones:

| Emotion        | Use Case             | Implementation                   |
| -------------- | -------------------- | -------------------------------- |
| **Neutral**    | Facts, introductions | exaggeration = 0.5 (baseline)    |
| **Excited**    | Discoveries          | exaggeration = 1.2 (high energy) |
| **Sad**        | Tragedies, loss      | exaggeration = 0.3 (subdued)     |
| **Serious**    | Critical info        | exaggeration = 0.4 (controlled)  |
| **Empathetic** | Human stories        | exaggeration = 0.6 (warm)        |
| **Urgent**     | Dramatic events      | exaggeration = 1.5 (intense)     |

**How it works:**

```python
# Map emotion + intensity to exaggeration value
base = emotion_map[emotion]  # "excited" = 1.2, "sad" = 0.3, etc.
exaggeration = 0.5 + intensity * (base - 0.5)
exaggeration = clamp(exaggeration, 0.25, 2.0)

audio = model.generate(text, exaggeration=exaggeration)
```

Way simpler than training emotion embeddings or prosody transfer. The model already knows how to sound expressive, I just dial it up/down.

---

## 4. Data Requirements

**For this prototype:** None! Chatterbox is already pre-trained.

**If I had budget for fine-tuning:**

- 50-100 hours of real documentary narration (BBC, PBS, Netflix)
- Would need licensing (~$10K-20K)
- Label emotions: mostly neutral (70%), some excited (15%), sad (5%), serious (8%), empathetic (2%)

**Why bother?**
Documentary narration is more subtle than audiobooks. Current models sound a bit theatrical. Fine-tuning on actual documentaries would fix that.

**Datasets that exist but aren't perfect:**

- RAVDESS - 7,356 emotional speech files (but it's acted, too dramatic)
- LibriTTS-R - 585 hours of audiobooks (neutral only)
- Neither really captures documentary style

---

## 5. Evaluation

### Objective Metrics (Automated)

| Metric               | Target   | How to Measure                         |
| -------------------- | -------- | -------------------------------------- |
| **MOS Score**        | > 4.0    | Crowdsourced listening tests (1-5)     |
| **Emotion Accuracy** | > 80%    | Trained classifier on output vs intent |
| **Intelligibility**  | < 5% WER | Whisper ASR on generated audio         |

### Subjective Testing

- A/B tests: AI vs human narrator (blind)
- Ask listeners: "Does the emotion fit the script?" (1-5)
- Need 20-50 people for statistical relevance

### What I Actually Did

Generated a bunch of samples, listened to them, tweaked parameters until they sounded decent. Not super scientific but good enough for prototyping. For real production I'd do proper MOS tests with 50+ people.

---

## 6. Deployment: "One Button" Tool

### CLI Tool (Current Implementation)

```bash
python solution.py "Hello world" output.wav
python solution.py "This is amazing!" output.wav --emotion excited --intensity 0.8
```

**Features:**

- Simple command-line interface
- Validates input (empty text, invalid emotions)
- Progress indicators
- Error handling with helpful messages

### Web Interface (Future)

For non-technical users:

- Text input box (paste script)
- Emotion dropdown (6 options)
- Intensity slider (0-100%)
- "Generate" button
- Download audio file

**Tech stack:** FastAPI backend + Streamlit/React frontend

### API (Also Implemented)

```bash
curl -X POST http://localhost:8000/v1/speech/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "emotion": "excited", "intensity": 0.8}'
```

Returns audio file URL for download.

---

## 7. Challenges & Limitations

### Challenge 1: Documentary "Feel" vs TTS Training Data

**Problem:** TTS models are trained on audiobooks and acted emotions. Documentary narration is different - more restrained, natural. My first tests sounded way too theatrical, like a stage play.

**What helped:**

- Tuned the exaggeration values down (e.g., "excited" = 1.2 instead of 2.0)
- Tested with real documentary scripts until it sounded right
- Ideally would fine-tune on actual BBC/PBS narration but that needs budget

### Challenge 2: Long-Form Consistency

**Problem:** TTS models can't handle infinite text, so I process in chunks (~500 tokens). For a 10-min script, the voice starts drifting - pitch changes, energy varies. It's subtle but noticeable.

**How to fix:**

- Keep 3-sentence context from previous chunk
- Don't reset emotion state between chunks
- Cross-fade chunks (50-100ms overlap)
- Haven't fully implemented this yet - current version works well for 1-2 min clips

### Challenge 3: Computational Cost

**Problem:** Good TTS needs GPU. On my M1 Mac, generating 1 min of audio takes ~15-20 sec. CPU only? More like 45 sec. If this gets popular with 100 users, cost adds up fast.

**Some ideas:**

- Batch multiple requests together
- Optimize with quantization / ONNX runtime (2x faster)
- Cache common phrases like "Welcome to..."
- For now CPU is fine for prototyping

### Challenge 4: Edge Cases

**Problem:** Numbers, acronyms, weird punctuation all trip up TTS. "2024", "NASA", "COVID-19" cause issues.

**My approach:**

- Normalize common stuff (2024 → "twenty twenty-four")
- Show helpful errors when things break
- Let users edit and retry

---

## 8. Conclusion

**What's working:**

- Chatterbox quality is surprisingly good
- 6 emotions handle most documentary scenarios
- Parameter mapping is simple (no ML expertise needed)
- Coqui fallback means fewer install failures

**What needs work:**

- Long-form (10+ min) consistency isn't there yet
- Could really use fine-tuning on real documentary audio
- Edge cases still trip it up sometimes
- Cost at scale needs optimization

---
