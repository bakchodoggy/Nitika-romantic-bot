from datetime import datetime

def format_profile(user_data):
    """Formats a user's profile details into a readable string."""
    lines = ["**Your Profile**"]
    keys = ["name", "mood", "fantasy", "heartbeats", "gems", "referrals"]

    for key in keys:
        value = user_data.get(key, "Not set" if key == "name" else "0" if key in ["heartbeats", "gems", "referrals"] else "Not selected")
        lines.append(f"{key.capitalize()}: {value}")

    if "joined" in user_data:
        lines.append(f"Joined: {user_data['joined']}")

    return "\n".join(lines)

def now_date():
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def trim_reply(text):
    """Cleans up replies by removing extra spaces and newlines."""
    return text.strip()

def send_typing_action(update, context):
    """Makes the bot show 'typing...' before sending a message."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

