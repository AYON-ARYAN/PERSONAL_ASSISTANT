EXIT_PHRASES = {
    "exit",
    "stop",
    "go to sleep",
    "bye",
    "goodbye",
    "thank you",
    "that's all",
    "shut down"
}

def is_exit_intent(text: str) -> bool:
    text = text.lower().strip()
    return any(phrase in text for phrase in EXIT_PHRASES)
