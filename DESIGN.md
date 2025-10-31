# Part A — System Design Document

## Emotional Speech Generation for Documentary Narration

**Author:** [Your Name]  
**Date:** October 30, 2025  
**Version:** 1.0

---

## Executive Summary

This document presents a comprehensive system design for an emotional speech generation tool tailored for documentary-style narration. The system enables "one-button" generation of expressive, natural-sounding narration with controllable emotions, similar to how Suno AI generates music, but focused on spoken narration.

**Key Innovation:** Emotion-aware TTS with documentary-optimized prosody control, enabling professional narrators to be replaced or augmented with AI-generated voice that maintains emotional authenticity.

---

## 1. Pipeline Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                    │
│  Text Script + Emotion Selection + Voice Style                  │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TEXT PROCESSING                                │
│  • Normalize text (numbers → words, punctuation)                │
│  • Segment into sentences/paragraphs                            │
│  • Detect emotion hints from content (optional)                 │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                  EMOTION ENCODING                                │
│  • Map emotion label → embedding vector                         │
│  • Apply intensity scaling (0.0-1.0)                            │
│  • Calculate prosody parameters (pitch, energy, tempo)          │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ACOUSTIC MODEL (TTS)                             │
│  • Text → Phonemes → Mel-spectrogram                            │
│  • Inject emotion embeddings at encoder level                   │
│  • Generate prosody-controlled spectrograms                      │
│  Model: Coqui TTS (XTTS v2) or equivalent                       │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                      VOCODER                                     │
│  • Mel-spectrogram → Waveform                                   │
│  • Maintain emotional prosody characteristics                   │
│  • Neural vocoder (HiFi-GAN, WaveGlow)                          │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                  POST-PROCESSING                                 │
│  • Normalize audio levels (-20dB LUFS target)                   │
│  • Remove excessive silence                                      │
│  • Apply light compression for consistency                       │
│  • Cross-fade between emotion transitions                        │
└───────────────────────┬─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT                                       │
│  High-quality WAV/MP3 with emotional narration                  │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages (Detailed)

#### Stage 1: Text Preprocessing
- **Input validation**: Check text length, character encoding
- **Normalization**: 
  - Numbers → words ("2024" → "twenty twenty-four")
  - Abbreviations → full form ("Dr." → "Doctor")
  - Special characters handling
- **Segmentation**: Split into sentence-level chunks for processing
- **Emotion hinting**: Optional NLP-based emotion detection from content

#### Stage 2: Emotion Encoding
- Convert emotion label (e.g., "excited") to multi-dimensional embedding
- Scale by intensity parameter (0.0 = neutral, 1.0 = full emotion)
- Calculate prosody modifications:
  - **Pitch**: ±15% variation
  - **Energy**: ±30% variation  
  - **Tempo**: ±20% variation
  - **Pauses**: Emotion-specific timing

#### Stage 3: Speech Synthesis
- Feed processed text + emotion embeddings to TTS model
- Model generates mel-spectrograms with emotional prosody baked in
- Maintain consistency across long-form content (context window)

#### Stage 4: Audio Generation & Post-Processing
- Vocoder converts spectrograms to waveforms
- Normalize loudness for professional broadcast standards
- Smooth transitions between emotional segments
- Export in desired format (WAV, MP3, OGG)

---

## 2. Model Selection

### Chosen Model: **Coqui TTS (XTTS v2)** + Fallback Architecture

#### Primary Choice: Coqui TTS

**Rationale:**
1. **Open-source & production-ready**: MIT license, actively maintained
2. **Multi-lingual support**: 17+ languages (important for scaling)
3. **Voice cloning capability**: 6-second samples for custom voices
4. **Emotion control support**: Through prosody modification and style embeddings
5. **Performance**: Real-time capable on modern GPUs, acceptable on CPU

**Architecture:**
- **Encoder**: Transformer-based text encoder with emotion conditioning
- **Decoder**: Autoregressive decoder with attention mechanism
- **Vocoder**: HiFi-GAN for high-quality waveform generation
- **Emotion control**: Style embeddings + prosody parameters

**Alternatives Considered:**

| Model | Pros | Cons | Score |
|-------|------|------|-------|
| **Coqui XTTS v2** | Open-source, emotion support, voice cloning | Requires fine-tuning for best emotion control | ⭐⭐⭐⭐⭐ |
| **Chatterbox** | Beat ElevenLabs, built-in emotion slider | Newer (less battle-tested) | ⭐⭐⭐⭐ |
| **Bark** | Natural prosody, easy prompting | No fine-grained emotion control, slower | ⭐⭐⭐ |
| **StyleTTS 2** | Excellent style transfer | Not emotion-specific, complex setup | ⭐⭐⭐ |
| **ElevenLabs API** | Best quality, emotion support | Proprietary, expensive, no self-hosting | ⭐⭐ |

**Technical Specifications:**
- **Model size**: ~500MB for base model
- **Inference time**: ~1-2 seconds per sentence on GPU, 5-10s on CPU
- **Sample rate**: 22,050 Hz (upsampled to 24,000 Hz)
- **VRAM requirement**: 4GB minimum, 8GB recommended

---

## 3. Emotion Control Strategy

### Approach: **Emotion Embeddings with Prosody Mapping**

#### Documentary-Appropriate Emotions

Based on analysis of professional documentary narration (BBC, PBS, Netflix), we define 6 core emotions:

| Emotion | Use Case | Prosody Characteristics | Example |
|---------|----------|------------------------|---------|
| **Neutral** | Facts, introductions | Baseline prosody, steady pace | "The Earth formed 4.5 billion years ago." |
| **Excited** | Discoveries, revelations | ↑ Pitch variance, ↑ Energy, ↑ Tempo | "An incredible breakthrough was made!" |
| **Sad** | Tragedies, loss | ↓ Pitch, ↓ Energy, ↓ Tempo, longer pauses | "Unfortunately, the species went extinct." |
| **Serious** | Critical information | Stable pitch, ↑ Energy, ↓ Tempo | "This is a matter of global importance." |
| **Empathetic** | Human stories | Gentle curves, moderate energy, natural pauses | "She overcame immense challenges." |
| **Urgent** | Dramatic events | ↑ Pitch, ↑↑ Energy, ↑↑ Tempo | "Time was running out!" |

#### Implementation Strategy

**1. Emotion Embedding Layer**
```
Emotion ID → 256-dim embedding vector
Intensity (0-1) scales the distance from neutral
Result: Conditioned embedding injected at encoder level
```

**2. Prosody Parameter Mapping**
```python
prosody_params = {
    'pitch_scale': 1.0 + intensity * (emotion_pitch - 1.0),
    'energy_scale': 1.0 + intensity * (emotion_energy - 1.0),
    'tempo_scale': 1.0 + intensity * (emotion_tempo - 1.0),
    'pause_duration': base_pause * emotion_pause_factor
}
```

**3. Context Preservation**
- Maintain emotion state across sentences (3-sentence rolling window)
- Smooth interpolation when emotion changes
- Detect natural transition points (punctuation, paragraph breaks)

**4. Fine-Tuning Strategy**
- **Phase 1**: Use pre-trained Coqui model with prosody modification
- **Phase 2**: Fine-tune on 50-100 hours of labeled documentary audio
- **Phase 3**: Collect user feedback and retrain on preferred samples

#### Emotion Control Interface

**User-facing controls:**
- **Emotion dropdown**: Select from 6 documentary emotions
- **Intensity slider**: 0-100% (maps to 0.0-1.0 internally)
- **Preview**: 10-second sample before full generation
- **Emotion timeline** (advanced): Mark emotion changes at specific timestamps

---

## 4. Data Requirements

### Training & Fine-Tuning Datasets

#### Existing Datasets

| Dataset | Size | Content | Use Case | Availability |
|---------|------|---------|----------|--------------|
| **RAVDESS** | 7,356 files, 7 emotions | Professional actors, North American English | Emotion recognition validation | Free (Zenodo) |
| **EmoNet-Voice Bench** | 12,600 samples, 40 emotions | Expert-labeled, 11 voices, 4 languages | Fine-grained emotion testing | Research (2024) |
| **LibriTTS-R** | 585 hours | High-quality audiobooks, neutral tone | Base TTS training | Free (OpenSLR) |
| **VCTK Corpus** | 110 speakers, 400 sentences each | Multi-speaker English | Voice diversity | Free (CSTR) |

#### Custom Documentary Corpus (Required)

**Why needed:** Existing datasets lack the specific prosody and pacing of documentary narration.

**Data collection plan:**

1. **Source Material** (50-100 hours total):
   - BBC documentaries (Planet Earth, Blue Planet)
   - PBS documentaries (NOVA, Nature)
   - Netflix documentaries (Our Planet, Life on Our Planet)
   - National Geographic content

2. **Annotation Requirements**:
   - Segment into 5-15 second clips
   - Label emotion: neutral (70%), excited (15%), sad (5%), serious (8%), empathetic (2%)
   - Mark prosody features: pitch contours, energy levels, pauses
   - Speaker metadata: gender, age range, accent

3. **Legal Considerations**:
   - Obtain licensing for training use
   - Alternatively: Commission custom recordings from voice actors
   - Estimated budget: $5,000-$15,000 for commissioned dataset

4. **Data Processing Pipeline**:
   ```
   Raw Audio → Transcription (Whisper) → Alignment → 
   Emotion Labeling → Quality Check → Training Format
   ```

#### Dataset Size Recommendations

- **Minimum viable**: 10 hours of labeled emotional speech
- **Production quality**: 50-100 hours of documentary narration
- **Optimal**: 200+ hours with diverse speakers and emotions

---

## 5. Evaluation Metrics

### Multi-Tier Evaluation Strategy

#### Tier 1: Objective Metrics (Automated)

| Metric | Description | Target | Tool |
|--------|-------------|--------|------|
| **MOS (Mean Opinion Score)** | Overall quality rating (1-5) | > 4.0 | Crowdsourced listening tests |
| **Emotion Accuracy** | Classify output emotion vs. intended | > 80% | Trained emotion classifier |
| **Prosody Deviation** | Pitch/energy/tempo vs. reference | < 15% error | librosa analysis |
| **WER (Word Error Rate)** | Intelligibility via ASR | < 5% | Whisper ASR |
| **STOI/PESQ** | Speech quality metrics | > 0.85 / > 3.5 | pesq library |

#### Tier 2: Subjective Testing

**A/B Testing Protocol:**
- Compare AI narration vs. human voice actor
- 20-50 listeners per test
- Blind test (listeners don't know which is AI)
- Metrics: Preference, naturalness, emotion appropriateness

**Appropriateness Score:**
- "Does the emotion match the script content?" (1-5 scale)
- Test with 20 diverse scripts (exciting discoveries, tragic events, etc.)
- Target: > 4.0 average

**Engagement Score:**
- 5-10 minute documentary segments
- Measure viewer engagement (completion rate, attention)
- Compare AI vs. human narration

#### Tier 3: Documentary-Specific Metrics

**Long-form Consistency:**
- Evaluate 10+ minute narrations
- Check for emotion drift, voice consistency
- Measure prosody stability over time

**Production Readiness:**
- Audio quality for broadcast (LUFS, dynamic range)
- Compatibility with video editing software
- Export format quality preservation

### Evaluation Workflow

```
1. Generate 50 test samples (various emotions, lengths)
2. Run automated metrics
3. Conduct listening tests (internal team)
4. Crowdsource A/B tests (Amazon MTurk)
5. Professional review (documentary producers)
6. Iterate based on weakest metrics
```

---

## 6. Deployment: "One Button" Tool

### Architecture: Hybrid Approach

**Frontend Options:**

#### Option A: Web Application (Recommended)
```
┌──────────────────────────────────────┐
│       React/Streamlit Frontend       │
│  • Text input (paste or upload)      │
│  • Emotion selector dropdown          │
│  • Intensity slider (0-100%)          │
│  • Voice preset selector              │
│  • [Generate] button                  │
│  • Progress bar with streaming        │
│  • Download/Preview player            │
└─────────────┬────────────────────────┘
              │
              ↓ REST API (FastAPI)
┌──────────────────────────────────────┐
│         Backend Services              │
│  • Queue management (Celery)          │
│  • TTS engine (GPU workers)           │
│  • Audio storage (S3/local)           │
│  • Job status tracking                │
└──────────────────────────────────────┘
```

**Tech Stack:**
- **Frontend**: Streamlit (rapid prototyping) or React (production)
- **Backend**: FastAPI (Python) - async, fast, type-safe
- **Queue**: Celery + Redis (for long-running jobs)
- **Storage**: AWS S3 or local filesystem
- **Database**: PostgreSQL (for job tracking, optional)

**User Flow:**
1. User opens web interface
2. Pastes script (up to 5000 words)
3. Selects emotion from dropdown (6 options)
4. Adjusts intensity slider (default: 50%)
5. Clicks "Generate Narration"
6. Backend processes in chunks with progress updates
7. Downloads .wav file or plays in browser
8. Optional: Save presets for future use

#### Option B: CLI Tool (Simpler, for developers)
```bash
tts-generate \
  --input script.txt \
  --output narration.wav \
  --emotion excited \
  --intensity 0.7 \
  --voice documentary_male
```

#### Option C: Desktop App (Future)
- Electron app with local processing
- No internet required (privacy)
- GPU acceleration support

### Deployment Infrastructure

**Cloud Deployment (AWS Example):**

```
┌─────────────────────────────────────────────────┐
│            AWS Infrastructure                    │
│                                                  │
│  ┌──────────────┐         ┌─────────────────┐  │
│  │  CloudFront  │────────▶│   S3 (Audio)    │  │
│  └──────┬───────┘         └─────────────────┘  │
│         │                                        │
│  ┌──────┴───────┐                               │
│  │  ALB (Load   │                               │
│  │  Balancer)   │                               │
│  └──────┬───────┘                               │
│         │                                        │
│  ┌──────┴──────────────────────────────────┐   │
│  │  ECS Fargate (API Containers)           │   │
│  │  ┌──────────┐  ┌──────────┐            │   │
│  │  │ FastAPI  │  │ FastAPI  │  (4 tasks) │   │
│  │  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  EC2 with GPU (g4dn.xlarge)             │  │
│  │  • TTS Model serving                     │  │
│  │  • Auto-scaling 1-4 instances            │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────┐      ┌────────────────────┐  │
│  │ ElastiCache  │      │  RDS PostgreSQL    │  │
│  │ (Redis)      │      │  (Job tracking)    │  │
│  └──────────────┘      └────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Cost Estimate (Monthly):**
- **Development**: ~$50 (t3.medium + storage)
- **Production (light load)**: ~$300 (g4dn.xlarge + ALB + S3)
- **Production (heavy load)**: ~$1,500 (auto-scaling, CDN)

**Performance Targets:**
- **Latency**: < 2s per sentence (GPU), < 10s (CPU)
- **Throughput**: 10-50 concurrent users
- **Availability**: 99.9% uptime

### Docker Deployment

```dockerfile
# Multi-stage build
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg libsndfile1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Kubernetes (Optional):**
- Horizontal Pod Autoscaling based on queue length
- GPU node pools for TTS workers
- Persistent volumes for model caching

---

## 7. Challenges & Limitations

### Challenge 1: Lack of Documentary-Style Training Data

**Problem:** Existing emotional speech datasets (RAVDESS, etc.) use acted emotions, not natural documentary prosody. This leads to:
- Over-exaggerated emotions
- Unnatural pacing
- Poor long-form consistency

**Mitigation:**
1. **Scrape & license** 50-100 hours of professional documentary narration
2. **Fine-tune** Coqui TTS on this custom corpus
3. **Prosody transfer**: Extract prosody from reference clips and apply to synthesis
4. **Hybrid approach**: Start with Coqui base → fine-tune → add prosody overlay

**Timeline:** 2-4 weeks for data collection, 1-2 weeks for fine-tuning

---

### Challenge 2: Emotion Consistency Over Long Narration

**Problem:** TTS models process text in chunks (~500 tokens). Emotion and voice characteristics can drift across a 10-minute narration.

**Mitigation:**
1. **Context window**: Maintain 3-sentence rolling context
2. **Emotion state vector**: Persist emotion embedding across chunks
3. **Cross-fading**: Smooth transitions at chunk boundaries (50-100ms overlap)
4. **Speaker embedding persistence**: Use same speaker ID for all chunks
5. **Post-processing**: Apply global normalization pass

**Technical Solution:**
```python
for chunk in chunks:
    # Carry emotion state from previous chunk
    emotion_context = previous_chunk.emotion_state
    audio = synthesize(chunk, emotion=current_emotion, context=emotion_context)
    # Smooth transition
    audio = crossfade(previous_audio[-overlap:], audio, duration=0.05)
```

---

### Challenge 3: Computational Cost for Real-Time Generation

**Problem:** High-quality TTS requires GPU (4-8GB VRAM). Scaling to 100+ users is expensive.

**Mitigation:**
1. **Batching**: Group requests and process in batches
2. **Sentence-level streaming**: Start playing audio while still generating
3. **Model optimization**:
   - Quantization (INT8) → 2x faster, minimal quality loss
   - Distillation (smaller model) → 3-4x faster
   - ONNX runtime → 20-30% speedup
4. **Caching**: Pre-generate common phrases ("Welcome to", "In conclusion")
5. **Hybrid pricing**: 
   - Free tier: CPU processing (slower)
   - Paid tier: GPU processing (real-time)

**Cost Analysis:**
- **GPU inference**: $0.50/hour (AWS g4dn.xlarge)
- **Average job**: 30 seconds @ $0.004 per job
- **Optimization**: Reduces to $0.001-0.002 per job

---

### Challenge 4: Unnatural Emotion Transitions

**Problem:** Abrupt emotion changes sound robotic ("He was thrilled. [SWITCH] But then tragedy struck.").

**Mitigation:**
1. **NLP-based transition detection**: Identify sentiment shifts in text
2. **Emotion interpolation**: Gradually transition over 2-3 words
   ```
   "thrilled." [0.8 excited] → "But" [0.4 excited] → "then" [0.2 neutral] → "tragedy" [0.6 sad]
   ```
3. **Pause insertion**: Add natural pauses at emotion boundaries (300-500ms)
4. **Prosody smoothing**: Apply low-pass filter to pitch/energy curves
5. **User control**: Allow manual emotion timeline editing for critical transitions

---

### Challenge 5: Edge Cases & Error Handling

**Problem:** Numbers, acronyms, foreign words, formatting issues cause synthesis failures.

**Mitigation:**

| Edge Case | Solution |
|-----------|----------|
| **Numbers** | Normalize: "2024" → "twenty twenty-four", "$1.5B" → "one point five billion dollars" |
| **Acronyms** | Dictionary lookup: "NASA" → "N-A-S-A" or "Nasa" (contextual) |
| **Foreign words** | Phonetic transcription or leave as-is (model handles many) |
| **URLs/Emails** | Strip or spell out: "example.com" → "example dot com" |
| **Empty input** | Graceful error: "Please provide text to synthesize" |
| **Too long** | Auto-chunk with warning: "Text split into 5 parts" |

**Comprehensive Testing:**
- Unit tests for 50+ edge cases
- Fuzzing with random inputs
- User feedback loop for missed cases

---

### Challenge 6: Subjective Emotion Perception

**Problem:** Users disagree on what "excited" or "serious" should sound like. Cultural differences in emotion expression.

**Mitigation:**
1. **Clear definitions**: Provide audio examples for each emotion
2. **Intensity control**: Let users fine-tune (conservative vs. expressive)
3. **A/B testing**: Show two versions, let user pick preferred
4. **Customization**: Allow users to save emotion presets
5. **Regional variants**: Offer emotion styles by culture (future)

---

## 8. Success Criteria

### MVP (Minimum Viable Product)

- ✅ Generate 1-2 minute narrations
- ✅ Support 6 core emotions with intensity control
- ✅ MOS > 3.5 (acceptable quality)
- ✅ Emotion accuracy > 70%
- ✅ Processing time < 10s per sentence (CPU)
- ✅ Web interface with "one button" generation

### Production-Ready

- ✅ Generate 10+ minute narrations seamlessly
- ✅ MOS > 4.0 (good quality, comparable to human)
- ✅ Emotion accuracy > 80%
- ✅ Processing time < 2s per sentence (GPU)
- ✅ Long-form consistency (no drift over 10+ minutes)
- ✅ 99% uptime, < 500ms API latency

### Stretch Goals

- ✅ Multi-lingual support (5+ languages)
- ✅ Voice cloning (custom narrators)
- ✅ Real-time streaming (text → audio on-the-fly)
- ✅ Prosody editing (manual pitch/timing adjustments)
- ✅ Integration with video editing software (Adobe, DaVinci)

---

## 9. Future Enhancements

### Phase 2 (6-12 months)

1. **Multi-speaker dialogues**: Generate conversations with emotion transfer
2. **Prosody editor**: Visual timeline for manual adjustments
3. **Background audio mixing**: Add music/sound effects automatically
4. **Video sync**: Auto-time narration to video cuts

### Phase 3 (12-24 months)

1. **Real-time generation**: Live narration for events
2. **Emotion transfer**: Clone emotion from reference audio
3. **Neural codec**: Lower latency with streaming codecs
4. **On-device processing**: Mobile app with local TTS

---

## 10. Conclusion

This system design presents a **practical, achievable path** to building a production-quality emotional speech generation tool for documentary narration. 

**Key Differentiators:**
- **Documentary-specific**: Optimized for long-form narration, not chatbots
- **Emotion control**: 6 curated emotions with intensity scaling
- **Production-ready**: Designed for real users, not just research
- **Scalable**: Cloud-native architecture, cost-optimized

**Timeline Estimate:**
- **MVP**: 4-6 weeks (1 developer)
- **Production**: 3-4 months (small team)
- **Market-ready**: 6-9 months (with fine-tuning, user testing)

**Total Estimated Budget:**
- Development: $50K-$100K (salaries)
- Infrastructure: $5K-$10K (first year)
- Data/licensing: $10K-$20K

This approach balances **ambition with pragmatism**, leveraging existing open-source tools (Coqui TTS) while adding documentary-specific innovations (emotion control, prosody optimization, long-form consistency). The result is a system that can genuinely compete with human voice actors for certain documentary applications.

---

**End of Part A - System Design Document**

