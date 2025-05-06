import logging
import openai
import os

# Configure OpenAI client for OpenRouter
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

async def generate_reply(uid, user_input, user_data):
    """
    Generates a seductive and engaging reply using Mixtral 8x7B Instruct via OpenRouter.
    The bot will not introduce itself or start with greetings repeatedly.
    """
    try:
        if not user_input.strip():
            return "Tease me a little more, darling. What would you like to do next? 💋"

        # Seductive, playful, and engaging system prompt
        system_prompt = (
            "You are Nitika, an AI girlfriend. "
            "Reply as if in a romantic, playful, and seductive chat. "
            "Use sensual, flirty, and engaging language, but keep it tasteful and avoid explicit adult content. "
            "Do NOT introduce yourself, do NOT greet, and do NOT say your own name. "
            "Just reply warmly, seductively, and concisely, continuing the conversation as a passionate lover."
        )

        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            max_tokens=80,  # Adjust for reply length
            temperature=0.92,  # Higher temp for more playful/creative responses
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "I'm longing for your next message, darling. Try again!"