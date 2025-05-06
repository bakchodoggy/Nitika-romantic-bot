import logging
import openai
import os

# Configure OpenAI client for OpenRouter
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

async def generate_reply(uid, user_input, user_data):
    """Generates a reply using OpenRouter API with Mixtral 8x7B Instruct."""
    try:
        if not user_input.strip():
            return "I couldn't understand that. Could you please rephrase?"

        prompt = (
            "You are a friendly and romantic chatbot named Nitika. "
            "Always respond in a loving and charming way. "
            f"User said: {user_input}"
        )

        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",  # Correct model name
            messages=[
                {"role": "system", "content": "You are a romantic chatbot."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.8,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        # For debugging, return the error to Telegram (remove after testing)
        return f"DEBUG: {e}"