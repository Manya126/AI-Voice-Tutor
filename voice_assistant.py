
import os
import time
import uuid
import numpy as np
import soundfile as sf
from gtts import gTTS
from faster_whisper import WhisperModel
from groq import Groq
import gradio as gr

# Load ASR
asr_model = WhisperModel("medium", device="cuda", compute_type="float16")

# Setup LLM
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_llm_response(text):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": """You are a helpful study tutor assistant. 
            Help students understand concepts clearly and concisely.
            Keep responses under 3 sentences for voice output."""},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, unique_id):
    mp3_path = f"/tmp/response_{unique_id}.mp3"
    wav_path = f"/tmp/response_{unique_id}.wav"
    gTTS(text=text, lang='en').save(mp3_path)
    os.system(f"ffmpeg -y -i {mp3_path} -ar 22050 -ac 1 {wav_path}")
    return wav_path

def voice_assistant(audio):
    try:
        if audio is None:
            return None, "No audio received", "Please record something"
        
        sample_rate, audio_data = audio
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        audio_data = audio_data.astype(np.float32)
        if np.abs(audio_data).max() > 1.0:
            audio_data = audio_data / 32768.0
        
        unique_id = str(uuid.uuid4())[:8]
        tmp_wav = f"/tmp/input_{unique_id}.wav"
        sf.write(tmp_wav, audio_data, sample_rate)
        
        t1 = time.time()
        segments, _ = asr_model.transcribe(tmp_wav, beam_size=5)
        transcript = " ".join([s.text for s in segments])
        t2 = time.time()
        
        if not transcript.strip():
            return None, "Could not hear anything", "Please speak clearly"
        
        response_text = get_llm_response(transcript)
        t3 = time.time()
        
        output_file = text_to_speech(response_text, unique_id)
        t4 = time.time()
        
        print(f"ASR: {t2-t1:.2f}s | LLM: {t3-t2:.2f}s | TTS: {t4-t3:.2f}s | Total: {t4-t1:.2f}s")
        
        return output_file, f"You said: {transcript}", f"Tutor: {response_text}"
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"Error: {str(e)}", "Please try again"

app = gr.Interface(
    fn=voice_assistant,
    inputs=gr.Audio(
        sources=["microphone", "upload"],
        type="numpy",
        label="🎤 Record or Upload your question"
    ),
    outputs=[
        gr.Audio(label="🔊 Tutor Response"),
        gr.Textbox(label="📝 Your Question"),
        gr.Textbox(label="🤖 Tutor Answer")
    ],
    title="🎓 AI Study Tutor — Voice Assistant",
    description="Record your question and get an instant voice response from your AI tutor!",
    flagging_mode="never"
)

if __name__ == "__main__":
    app.launch(share=True)
