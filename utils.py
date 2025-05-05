from datetime import datetime
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

def format_profile(user_data):
    """Formats a user's profile details into a readable string."""
    try:
        lines = ["**Your Profile**"]
        keys = ["name", "mood", "fantasy", "heartbeats", "gems", "referrals"]

        for key in keys:
            value = user_data.get(key, "Not set" if key == "name" else "0" if key in ["heartbeats", "gems", "referrals"] else "Not selected")
            lines.append(f"{key.capitalize()}: {value}")

        if "joined" in user_data:
            lines.append(f"Joined: {user_data['joined']}")

        return "\n".join(lines)
    except Exception as e:
        logging.error(f"Error formatting profile: {e}", exc_info=True)
        return "Error retrieving profile information."

def now_date():
    """Returns the current date in YYYY-MM-DD format."""
    try:
        return datetime.now().strftime("%Y-%m-%d")
    except Exception as e:
        logging.error(f"Error fetching current date: {e}", exc_info=True)
        return "Unknown Date"

def trim_reply(text, max_length=200):
    """Cleans up replies by removing extra spaces and newlines, and trims to a maximum length."""
    try:
        if not text:
            return "Something went wrong while generating a reply. Please try again!"
        text = text.strip()
        return text[:max_length] + "..." if len(text) > max_length else text
    except Exception as e:
        logging.error(f"Error trimming reply: {e}", exc_info=True)
        return "Error processing the reply."

async def send_typing_action(update, context):
    """Makes the bot show 'typing...' before sending a message."""
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except Exception as e:
        logging.error(f"Error sending typing action: {e}", exc_info=True)