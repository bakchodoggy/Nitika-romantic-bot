import logging
import openai  # Ensure the OpenAI library is installed
import os

# Configure OpenAI client to use OpenRouter endpoint
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

async def generate_reply(uid, user_input, user_data):
    """Generates a reply using OpenRouter API and AI-based logic."""
    try:
        if not user_input.strip():
            return "I couldn't understand that. Could you please rephrase?"

        # You can adjust the prompt as needed for your bot
        prompt = (
            "You are a friendly and romantic chatbot named Nitika. "
            "Always respond in a loving and charming way. "
            f"User said: {user_input}"
        )

        # Call OpenRouter API via OpenAI library
        response = openai.ChatCompletion.create(
            # Use an OpenRouter model name, for example:
            model="openrouter/anthropic/claude-3-haiku",  # Change to your preferred model
            messages=[
                {"role": "system", "content": "You are a romantic chatbot."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.8,
        )

        # Extract the AI-generated reply
        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "I'm having trouble responding romantically right now. Please try again!"