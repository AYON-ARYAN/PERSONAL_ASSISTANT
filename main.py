from stt.record import record_audio
from stt.transcribe import transcribe
from llm.ollama_client import ask_llm
from tts.speak import speak

AUDIO = "audio/input.wav"

while True:
    record_audio(AUDIO)
    text = transcribe(AUDIO)

    if not text:
        continue

    print("🧠 You:", text)

    reply = ask_llm(text)
    print("🤖 AI:", reply)

    speak(reply)
