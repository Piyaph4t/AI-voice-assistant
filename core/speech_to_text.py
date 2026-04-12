import speech_recognition as sr
from faster_whisper import WhisperModel
import numpy as np

r = sr.Recognizer()
model = WhisperModel("tiny.en", device="cpu",compute_type="int8")


# =========================
# 🧠 Speech Recognition (Whisper)
# =========================
def listen_and_transcribe(duration=5):

    global model
    with sr.Microphone(sample_rate=16000) as source:
        print("🎤 Speak...")
        audio = r.listen(source)

    # convert audio to numpy
    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    audio_data = audio_data.astype(np.float32) / 32768.0

    segments, _ = model.transcribe(audio_data)

    return ' '.join([seg.text for seg in segments])


