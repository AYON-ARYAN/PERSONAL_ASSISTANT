import subprocess

def speak(text):
    subprocess.run(["say", text])
