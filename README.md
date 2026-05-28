# 🎓 AI Study Tutor — Voice Assistant

## What it does
Students struggle to get instant answers to study questions outside classroom hours. This voice assistant lets a student speak any academic question and receive a clear spoken response in real time — no typing needed. The pipeline is: **Speech → Text → AI Reasoning → Voice Response.**

## Demo Screenshot
![AI Study Tutor Demo](Screenshot%20(1255).png)

## Why I built this
I chose this because I've personally mentored underprivileged students through the Desh Ka Mentor program and seen how many lack access to on-demand academic help. A voice-first tutor removes barriers for students who struggle with typing or have limited resources. This felt like a problem worth solving — not just a technical exercise.

## How to run it

```bash
# Install dependencies
pip install -r requirements.txt
apt-get install -y ffmpeg

# Set API key
export GROQ_API_KEY="your_groq_api_key_here"

# Run
python voice_assistant.py
```

## Pipeline Architecture
**ASR → LLM → TTS**

| Stage | Model | Latency |
|-------|-------|---------|
| ASR | Whisper Medium (faster-whisper, float16) | ~0.72s |
| LLM | LLaMA 3.1 8B via Groq API | ~0.32s |
| TTS | gTTS + ffmpeg | ~4.27s |
| **Total** | **End-to-end** | **~5.30s** |

## Architecture Decisions

**ASR — Whisper Medium over Parakeet**
Chose faster-whisper with float16 quantization on GPU. Whisper medium gave 0.72s latency which is acceptable for natural conversation. Parakeet required additional NVIDIA NeMo setup which added unnecessary complexity for a 5-day build.

**LLM — Groq API over local model**
Running Sarvam-30B or Qwen3-27B locally would consume all 24GB VRAM leaving none for ASR and TTS. Groq's free API gives 0.32s response time — faster than any local model would achieve on this hardware.

**TTS — gTTS over Voxtral TTS**
Voxtral TTS required complex model setup. gTTS is reliable and produces natural speech. The 4.27s latency is the main bottleneck — would replace with a local neural TTS in production.

**UUID-based temp filenames**
Initially used fixed `/tmp/input.wav` filename which caused a critical caching bug — every question returned the same answer regardless of what was asked. Fixed by generating unique filenames per request using UUID.

## What I used AI for

**AI generated:**
- Gradio UI boilerplate and layout
- Initial system prompt template for tutor persona
- ffmpeg conversion flag suggestions

**Written by hand:**
- Audio normalization pipeline (stereo→mono, float32 conversion)
- UUID-based file management to prevent caching bugs
- Per-stage latency measurement system
- Pipeline integration logic

**Where I overrode AI:**
- AI suggested verbose, hedge-heavy system prompts — I shortened to "under 3 sentences for voice output" which dramatically improved response quality for audio playback
- AI suggested keeping fixed filenames for simplicity — I overrode this after discovering the caching bug causing wrong answers

## What I would change with 4 more weeks
1. **Replace gTTS with Coqui TTS** — cut TTS latency from 4.27s to under 1s
2. **Add streaming ASR** — start processing while user is still speaking, reduce perceived latency
3. **RAG over NCERT textbooks** — grounded subject-specific answers instead of general LLM responses
4. **Conversation memory** — multi-turn dialogue so student can ask follow-up questions
5. **Mobile app** — React Native wrapper for offline use in low-connectivity areas in India

## Sample Transcript
**Student asks:** *"What is machine learning?"*

**Tutor responds:** *"Machine learning is a subset of artificial intelligence that involves training algorithms to learn from data and make predictions or decisions without being explicitly programmed. It allows computers to improve their performance on a task over time, based on the data they receive. Think of it like a student improving their math skills through practice."*

## Tech Stack
- **ASR:** faster-whisper (Whisper Medium, float16)
- **LLM:** LLaMA 3.1 8B via Groq API
- **TTS:** gTTS + ffmpeg
- **UI:** Gradio
- **GPU:** NVIDIA A30 24GB on JarvisLabs
- **Deployment:** JarvisLabs + Gradio public URL
