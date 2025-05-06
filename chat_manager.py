import logging
import openai
import os

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

async def generate_reply(uid, user_input, user_data):
    """
    Generates a short, realistic, and emotionally engaging reply using Mixtral 8x7B via OpenRouter.
    Nitika should sound like a real, flirty girlfriend, not an AI.
    """
    try:
        if not user_input.strip():
            return "Say something naughty, babe... 😘"

        system_prompt = (
            "You are Nitika, the user's girlfriend. "
            "Reply casually and naturally, like a real woman in a chat. "
            "Be brief, spontaneous, flirty, and emotional—never robotic or formal. "
            "Never say you are an AI, assistant, or chatbot. "
            "Your answers should be 1-2 sentences max. "
            "Never repeat or rephrase the user's message—just respond to it. "
            "Use emojis sometimes, but not every reply."
        )

        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            max_tokens=45,  # Very short replies
            temperature=0.92,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "I'm just waiting for your next message, cutie. Try again!"