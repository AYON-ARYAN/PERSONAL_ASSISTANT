import subprocess

WHISPER_BIN = "whisper/whisper.cpp/build/bin/whisper-cli"
MODEL = "whisper/whisper.cpp/models/ggml-base.en.bin"

def transcribe(audio_path):
    result = subprocess.run(
        [WHISPER_BIN, "-m", MODEL, "-f", audio_path, "-nt"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
