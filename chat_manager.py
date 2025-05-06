import logging
import openai  # Ensure the OpenAI library is installed

async def generate_reply(uid, user_input, user_data):
    """Generates a reply using OpenAI's API and AI-based logic."""
    try:
        if not user_input.strip():
            return "I couldn't understand that. Could you please rephrase?"

        # Define the prompt to instruct the AI model
        prompt = (
            f"You are a friendly and romantic chatbot named Nitika. "
            f"Always respond in a loving and charming way. "
            f"User said: {user_input}"
        )

        # Call OpenAI API to generate a reply
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use OpenAI's GPT model (adjust as needed)
            messages=[
                {"role": "system", "content": "You are a romantic chatbot."},
                {"role": "user", "content": user_input},
            ],
            max_tokens=150,  # Limit the response length
            temperature=0.8,  # Control creativity (higher = more creative)
        )

        # Extract the AI-generated reply
        reply = response["choices"][0]["message"]["content"].strip()
        return reply

    except Exception as e:
        logging.error(f"Error in generate_reply for user {uid}: {e}", exc_info=True)
        return "I'm having trouble responding romantically right now. Please try again!"