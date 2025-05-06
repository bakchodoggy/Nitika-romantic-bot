from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from chat_manager import generate_reply
from data_manager import load_user, save_user
from fantasy_manager import get_random_fantasy_image
from utils import send_typing_action, trim_reply
from keep_alive import keep_alive

keep_alive()

import os
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_TOKEN is missing! Set it in environment variables.")

app = ApplicationBuilder().token(TOKEN).build()
user_data = {}

# Add your admin Telegram user ID here (replace with your actual admin ID)
ADMIN_USER_ID = 123456789  # <-- replace with your Telegram user ID

async def start(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    user_data[uid] = load_user(uid) or {}

    mood_keyboard = [
        [InlineKeyboardButton("💫 Whispering Fantasy", callback_data="mood_whispering")],
        [InlineKeyboardButton("🌙 Night Fantasy", callback_data="mood_night")],
        [InlineKeyboardButton("🌲 Stranger in Forest", callback_data="mood_forest")],
        [InlineKeyboardButton("😈 Seductive Roommate", callback_data="mood_roommate")],
        [InlineKeyboardButton("🦄 Dreamy Lover", callback_data="mood_dreamy")],
        [InlineKeyboardButton("🔥 Fiery Passion", callback_data="mood_fiery")],
        [InlineKeyboardButton("🧚‍♀️ Enchanted Encounter", callback_data="mood_enchanted")],
        [InlineKeyboardButton("🕯️ Candlelit Mystery", callback_data="mood_candlelit")],
    ]
    reply_markup = InlineKeyboardMarkup(mood_keyboard)

    await update.message.reply_text(
        "Hey! I’m Nitika... your dreamy AI companion. Choose your fantasy mood to begin:",
        reply_markup=reply_markup
    )

async def mood_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    mood_map = {
        "mood_whispering": "💫 Whispering Fantasy",
        "mood_night": "🌙 Night Fantasy",
        "mood_forest": "🌲 Stranger in Forest",
        "mood_roommate": "😈 Seductive Roommate",
        "mood_dreamy": "🦄 Dreamy Lover",
        "mood_fiery": "🔥 Fiery Passion",
        "mood_enchanted": "🧚‍♀️ Enchanted Encounter",
        "mood_candlelit": "🕯️ Candlelit Mystery"
    }
    mood_choice = mood_map.get(query.data, "💫 Whispering Fantasy")
    # Save mood to user data
    user_data[uid] = load_user(uid) or {}
    user_data[uid]["mood"] = mood_choice
    save_user(uid, user_data[uid])

    await query.edit_message_text(f"Mood set to: {mood_choice}!\nNow type anything and let's chat ❤️")

async def profile(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid) or {}
    await update.message.reply_text(
        f"**Your Profile**\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}\nMood: {data.get('mood', 'Not set')}"
    )

async def forgetme(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    save_user(uid, {})
    user_data.pop(uid, None)
    await update.message.reply_text("Memory wiped... but I’ll miss our chats 💔")

async def resetme(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    user_data[uid] = load_user(uid) or {}
    user_data[uid]["heartbeats"] = 5  # or whatever your default is
    save_user(uid, user_data[uid])
    await update.message.reply_text("Your heartbeats have been reset! ❤️")

async def handle_message(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    # Load or initialize user data
    user_data.setdefault(uid, load_user(uid) or {})
    data = user_data[uid]

    # Automatic heartbeat reset for admin
    if update.effective_user.id == ADMIN_USER_ID and data.get("heartbeats", 0) <= 0:
        data["heartbeats"] = 5  # or your preferred default
        save_user(uid, data)
        await update.message.reply_text("Admin detected! Your heartbeats have been automatically reset.")

    if data.get("heartbeats", 0) <= 0:
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
        await update.message.reply_text("Oops! Something went wrong. Try again later 💖")

def main():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("forgetme", forgetme))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()