import requests
from utils import trim_reply

API_KEY = "your_openrouter_api_key"
MODEL = "mistralai/mixtral-8x7b-instruct"

chat_memory = {}

def get_messages(uid, user_input):
    history = chat_memory.get(uid, [])
    history.append({"role": "user", "content": user_input})
    history = history[-5:]
    chat_memory[uid] = history
    return history

async def generate_reply(uid, user_input, data):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = "You are Nitika, a seductive, flirty, romantic AI girlfriend who replies in an emotionally engaging, playful, and safe manner. Avoid formal tone. No Hinglish. English only."

    if data.get("fantasy_mode"):
        system_prompt += " Speak like a mysterious stranger in a romantic fantasy."

    messages = [{"role": "system", "content": system_prompt}] + get_messages(uid, user_input)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.9
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]
    chat_memory[uid].append({"role": "assistant", "content": reply})
    return trim_reply(reply)
