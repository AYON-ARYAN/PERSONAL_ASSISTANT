import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def record_audio(path, seconds=4, fs=16000):
    print("🎙 Speak now...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    write(path, fs, audio)
