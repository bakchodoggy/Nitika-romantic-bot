import logging
import openai
import os

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

def get_chat_history(user_data, user_input=None, window=5):
    """
    Returns OpenAI-style message history from user_data.
    Keeps last `window` turns (user+assistant). Optionally appends the current user_input.
    """
    history = user_data.get("history", [])
    messages = []
    for role, text in history[-window*2:]:
        messages.append({"role": role, "content": text})
    if user_input is not None:
        messages.append({"role": "user", "content": user_input})
    return messages

async def generate_reply(uid, user_input, user_data):
    """
    Generates a short, realistic, and emotionally engaging reply using Mixtral 8x7B via OpenRouter.
    Nitika sounds like a real girlfriend, not an AI, and stays in context.
    """
    try:
        if not user_input.strip():
            return "Say something... I'm waiting. 🥰"

        system_prompt = (
            "You are Nitika, the user's girlfriend. "
            "Reply like a real, flirty, attentive girlfriend texting in a chat. "
            "Be natural, casual, spontaneous, and emotionally expressive—never robotic or formal. "
            "Always answer directly to what the user just said, and keep the conversation realistic, on-topic, and in context. "
            "Don't say you are an AI or chatbot, don't introduce yourself, don't repeat the user's message. "
            "Use up to 4-5 lines if needed, but no more. "
            "Sometimes use emojis, but not every message. "
            "Do NOT include any notes, instructions, or meta-comments in your replies."
        )

        # Always start with system prompt, then the last 5 turns + current input
        messages = [{"role": "system", "content": system_prompt}]
        messages += get_chat_history(user_data, user_input, window=5)

        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=messages,
            max_tokens=120,   # Allows up to 4-5 lines
            temperature=0.88,
        )

        reply = response["choices"][0]["message"]["content"].strip()

        # If the reply contains any "Note:" or system prompt leakage, remove it.
        if "Note:" in reply:
            reply = reply.split("Note:")[0].strip().rstrip("()").strip()

        # Save to history for next time (truncate if needed)
        history = user_data.get("history", [])
        history.append(("user", user_input))
        history.append(("assistant", reply))
        user_data["history"] = history[-10:]  # keep last 5 exchanges

        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "Something went wrong… but I'm still here for you! Try again?"