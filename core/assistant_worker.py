from PySide6.QtCore import QObject, Signal
import time

from stt.record import record_audio
from stt.transcribe import transcribe
from llm.ollama_client import ask_llm
from tts.speak import speak
from core.conversation import is_exit_intent
from core.memory import ConversationMemory


class AssistantWorker(QObject):
    listening = Signal()
    thinking = Signal()
    speaking = Signal(str)
    session_ended = Signal()   # ✅ ADD THIS SIGNAL

    def __init__(self):
        super().__init__()
        self.running = True
        self.audio_path = "audio/input.wav"
        self.session_active = False
        self.memory = ConversationMemory()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:

            # 🔹 Start a new conversation session
            self.session_active = True
            self.memory.clear()
            last_activity = time.time()

            while self.session_active:

                # 🎙 LISTENING
                self.listening.emit()
                record_audio(self.audio_path)

                user_text = transcribe(self.audio_path)

                # ⏳ TIMEOUT CASE (NO SPEECH)
                if not user_text.strip():
                    if time.time() - last_activity > 25:
                        self.session_active = False
                        self.session_ended.emit()   # ✅ EMIT HERE
                    continue

                last_activity = time.time()

                # 🚪 EXIT INTENT
                if is_exit_intent(user_text):
                    goodbye = "Alright, I’ll stop listening."
                    self.speaking.emit(goodbye)
                    speak(goodbye)

                    self.session_active = False
                    self.session_ended.emit()       # ✅ EMIT HERE
                    break

                # 🧠 NORMAL CONVERSATION
                self.memory.add_user(user_text)

                self.thinking.emit()
                prompt = self.memory.build_prompt(user_text)
                reply = ask_llm(prompt)

                self.memory.add_assistant(reply)

                self.speaking.emit(reply)
                speak(reply)

            time.sleep(1)
