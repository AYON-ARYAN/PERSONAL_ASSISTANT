from actions.open_app import open_app

def execute(intent_data):
    intent = intent_data.get("intent")

    if intent == "open_app":
        open_app(intent_data.get("app"))
        return f"Opening {intent_data.get('app')}"

    elif intent == "system_info":
        return "You are running macOS."

    return intent_data.get("response", "Okay.")
