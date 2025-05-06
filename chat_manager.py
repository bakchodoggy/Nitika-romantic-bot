import logging
import openai
import os

# Configure OpenAI client for OpenRouter
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

async def generate_reply(uid, user_input, user_data):
    """
    Generates a romantic and concise reply using Mixtral 8x7B Instruct via OpenRouter.
    The bot will not introduce itself or start with greetings repeatedly.
    """
    try:
        if not user_input.strip():
            return "Could you say that again? 💖"

        # This system prompt keeps the tone romantic and concise, no intros/greetings.
        system_prompt = (
            "You are Nitika, an AI girlfriend. "
            "Reply as if in a romantic, playful, and affectionate chat. "
            "Do NOT introduce yourself, do NOT greet, and do NOT say your own name. "
            "Just reply warmly and concisely as if continuing a conversation."
        )

        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            max_tokens=80,  # Shorter replies
            temperature=0.85,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "I'm having trouble responding romantically right now. Please try again!"