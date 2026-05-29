# 🎓 AI Study Tutor — Voice Assistant

## What it does
Students struggle to get instant answers to study questions outside classroom hours. This voice assistant lets a student speak any academic question and receive a clear spoken response in real time — no typing needed. The pipeline is: **Speech → Text → AI Reasoning → Voice Response.**

## Demo Screenshot
![AI Study Tutor Demo](Screenshot%20(1255).png)

## 🎯 Live Demo
**Try it yourself:** https://c506c12ec5e8027062.gradio.live/

**Sample audio files to test:**
- Upload `My_audio.wav` — sample question audio
- Expected response audio: `AI_Tutor_Response.wav`

## Why I built this
I chose this because I've personally mentored underprivileged students through the Desh Ka Mentor program and seen how many lack access to on-demand academic help. A voice-first tutor removes barriers for students who struggle with typing or have limited resources. This felt like a problem worth solving — not just a technical exercise.

## How to run it

```bash
# Install dependencies
pip install -r requirements.txt

# Install ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
cp ffmpeg-*-amd64-static/ffprobe /usr/local/bin/

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

### What I did to reduce latency
- Used **float16 quantization** on Whisper — reduced ASR latency by ~40%
- Used **Groq API** instead of local LLM — 0.32s vs 3-5s for local inference
- Used **beam_size=5** for Whisper — best accuracy/speed tradeoff
- Main bottleneck is TTS at 4.27s — would replace gTTS with Coqui TTS in production to get under 1s

## Architecture Decisions

**ASR — Whisper Medium over Parakeet**
Chose faster-whisper with float16 quantization on GPU. Whisper medium gave 0.72s latency which is acceptable. Parakeet required additional NVIDIA NeMo setup which added unnecessary complexity for a 5-day build.

**LLM — Groq API over local model**
Running Sarvam-30B or Qwen3-27B locally would consume all 24GB VRAM leaving none for ASR and TTS. Groq's free API gives 0.32s response time — faster than any local model on this hardware.

**TTS — gTTS over Voxtral TTS**
Voxtral TTS required complex model setup. gTTS is reliable and produces natural speech. The 4.27s latency is the main bottleneck — would replace with Coqui TTS in production.

**UUID-based temp filenames**
Initially used fixed `/tmp/input.wav` causing a critical caching bug — every question returned the same answer. Fixed by generating unique filenames per request using UUID.

## Sample Transcript

**Student asks:** *"What is the capital of India?"*

**Tutor responds:** *"The capital of India is New Delhi. It is located in the northern part of the country and is a major cultural and economic hub."*

---

**Student asks:** *"What is machine learning?"*

**Tutor responds:** *"Machine learning is a subset of artificial intelligence that involves training algorithms to learn from data and make predictions without being explicitly programmed. It allows computers to improve their performance on a task over time based on the data they receive."*

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
- AI suggested verbose system prompts — shortened to "under 3 sentences for voice output" which dramatically improved audio response quality
- AI suggested fixed filenames — overrode after discovering caching bug causing wrong answers

## What I would change with 4 more weeks
1. **Replace gTTS with Coqui TTS** — cut TTS latency from 4.27s to under 1s
2. **Add streaming ASR** — start processing while user is still speaking
3. **RAG over NCERT textbooks** — grounded subject-specific answers
4. **Conversation memory** — multi-turn dialogue for follow-up questions
5. **Mobile app** — React Native wrapper for low-connectivity areas in India

## Tech Stack
- **ASR:** faster-whisper (Whisper Medium, float16)
- **LLM:** LLaMA 3.1 8B via Groq API
- **TTS:** gTTS + ffmpeg
- **UI:** Gradio
- **GPU:** NVIDIA A30 24GB on JarvisLabs
- **Deployment:** JarvisLabs + Gradio public URL
