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

from keep_alive import keep_alive

# Start the keep-alive server for 24/7 uptime
keep_alive()

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load Telegram bot token securely
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_TOKEN is missing! Set it in environment variables.")

app = ApplicationBuilder().token(TOKEN).build()
user_data = {}

async def start(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    user_data[uid] = load_user(uid) or {}
    await update.message.reply_text(
        "Hey! I’m Nitika... your dreamy AI companion. Type anything, and let's chat ❤️"
    )

async def profile(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid) or {}
    await update.message.reply_text(
        f"**Your Profile**\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}"
    )

async def forgetme(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    save_user(uid, {})
    user_data.pop(uid, None)
    await update.message.reply_text("Memory wiped... but I’ll miss our chats 💔")

async def handle_message(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    # Load or initialize user data
    user_data.setdefault(uid, load_user(uid) or {})
    data = user_data[uid]
    if "heartbeats" not in data:
        data["heartbeats"] = 5  # Default number of heartbeats

    if data["heartbeats"] <= 0:
        await update.message.reply_text(
            "You're out of heartbeats! Invite a friend or buy more to continue."
        )
        return

    await send_typing_action(update, context)

    try:
        user_input = update.message.text
        logging.info(f"User Input from {uid}: {user_input}")

        reply = await generate_reply(uid, user_input, data)
        logging.info(f"Generated Reply: {reply}")

        if not reply or reply.strip() == "":
            raise ValueError("Generated reply is empty or invalid.")

        # Send the AI reply
        await update.message.reply_text(reply)

        # Fantasy mode (optional image)
        if data.get("fantasy_mode"):
            image = get_random_fantasy_image()
            if image:
                logging.info(f"Fantasy Image URL: {image}")
                await update.message.reply_photo(photo=image)
            else:
                logging.warning(f"No fantasy image returned for user {uid}.")

        # Deduct a heartbeat and save user data
        data["heartbeats"] -= 1
        save_user(uid, data)
        logging.info(
            f"User {uid} data saved successfully. Remaining heartbeats: {data['heartbeats']}"
        )

    except ValueError as ve:
        logging.warning(f"ValueError in handle_message for user {uid}: {ve}")
        await update.message.reply_text("Sorry, I couldn't process your input. Please try again!")
    except Exception as e:
        logging.error(f"Error in handle_message for user {uid}: {e}", exc_info=True)
        # Show the real error in Telegram temporarily (remove or comment out in production)
        await update.message.reply_text(f"DEBUG: {e}")

def main():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("forgetme", forgetme))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()