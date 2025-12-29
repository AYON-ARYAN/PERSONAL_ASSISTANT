import json
from llm.ollama_client import ask_llm

def parse_intent(user_text):
    with open("core/intent_prompt.txt") as f:
        prompt = f.read().replace("{{USER_INPUT}}", user_text)

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {"intent": "chat", "response": response}
