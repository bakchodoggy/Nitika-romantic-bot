import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackContext
)
from chat_manager import generate_reply
from data_manager import load_user, save_user
from fantasy_manager import get_random_fantasy_image
from utils import send_typing_action, trim_reply

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load Telegram bot token securely
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ensure token is set
if not TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_TOKEN is missing! Set it in environment variables.")

# Create application (NO Updater object)
app = ApplicationBuilder().token(TOKEN).build()

user_data = {}

async def start(update: Update, context: CallbackContext):
    """Handles /start command."""
    uid = str(update.effective_user.id)
    user_data[uid] = load_user(uid) or {}

    await update.message.reply_text(
        "Hey! I’m Nitika... your dreamy AI companion. Type anything, and let's chat ❤️"
    )

async def profile(update: Update, context: CallbackContext):
    """Handles /profile command to show user data."""
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid)

    await update.message.reply_text(
        f"**Your Profile**\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}"
    )

async def forgetme(update: Update, context: CallbackContext):
    """Handles /forgetme command to wipe user data."""
    uid = str(update.effective_user.id)
    save_user(uid, {})
    user_data.pop(uid, None)

    await update.message.reply_text("Memory wiped... but I’ll miss our chats 💔")

# Updated handle_message function with logging
async def handle_message(update: Update, context: CallbackContext):
    """Handles user messages and generates a reply."""
    uid = str(update.effective_user.id)
    user_data.setdefault(uid, load_user(uid))
    data = user_data[uid]

    if data.get("heartbeats", 5) <= 0:
        await update.message.reply_text(
            "You're out of heartbeats! Invite a friend or buy more to continue."
        )
        return

    await send_typing_action(update, context)

    try:
        user_input = update.message.text
        reply = await generate_reply(uid, user_input, data)
        reply = trim_reply(reply)  # Trimming overly long replies

        await update.message.reply_text(reply)

        if data.get("fantasy_mode"):
            image = get_random_fantasy_image()
            if image:
                await update.message.reply_photo(photo=image)

        data["heartbeats"] -= 1
        save_user(uid, data)

    except Exception as e:
        logging.error(f"Error in handle_message: {e}")
        await update.message.reply_text("Oops! Something went wrong. Try again later 💖")

# Adding handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("forgetme", forgetme))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Start bot with polling (Updater is REMOVED)
print("Bot is running...")
app.run_polling()