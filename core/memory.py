class ConversationMemory:
    def __init__(self, max_turns=6):
        self.max_turns = max_turns
        self.history = []

    def add_user(self, text):
        self.history.append(f"User: {text}")
        self._trim()

    def add_assistant(self, text):
        self.history.append(f"Assistant: {text}")
        self._trim()

    def _trim(self):
        # Keep only last N turns (user+assistant = 2 entries)
        max_entries = self.max_turns * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]

    def clear(self):
        self.history = []

    def build_prompt(self, user_input):
        context = "\n".join(self.history)
        return f"""You are a helpful offline voice assistant.

Conversation so far:
{context}

User: {user_input}
Assistant:"""
