import os
import requests
from utils import trim_reply

API_KEY = os.getenv("OPENROUTER_API_KEY")  # Secure API key handling
MODEL = "mistralai/mixtral-8x7b-instruct"

chat_memory = {}

def get_messages(uid, user_input):
    history = chat_memory.get(uid, [])
    history.append({"role": "user", "content": user_input})

    # Limit memory size efficiently
    chat_memory[uid] = history[-5:]
    return chat_memory[uid]

async def generate_reply(uid, user_input, data):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = "You are Nitika, a playful, emotionally engaging AI girlfriend. No formal tone. English only."
    
    if data.get("fantasy_mode"):
        system_prompt += " Speak like a mysterious stranger in a romantic fantasy."

    messages = [{"role": "system", "content": system_prompt}] + get_messages(uid, user_input)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={"model": MODEL, "messages": messages, "max_tokens": 300, "temperature": 0.9}
        )

        # Handle API errors gracefully
        if response.status_code != 200:
            return "Oops! Something went wrong. Try again later. ❤️"

        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "I’m here to chat, love!")
        chat_memory[uid].append({"role": "assistant", "content": reply})
        return trim_reply(reply)

    except Exception as e:
        return f"Error generating reply: {str(e)}"
