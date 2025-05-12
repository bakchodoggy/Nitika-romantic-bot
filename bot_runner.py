import os
import logging
import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from chat_manager import generate_reply
from fantasy_manager import get_random_fantasy_image
from utils import send_typing_action, trim_reply

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = 1444093362

# Set your FastAPI backend URL here
BACKEND_BASE_URL = "https://site--nitika-romantic-bot--87r4gwyv9z7f.code.run"

logging.basicConfig(level=logging.INFO)

user_data = {}

async def api_post(endpoint, payload):
    url = f"{BACKEND_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()
        return res.json()

async def get_user_api(uid):
    return await api_post("/api/user", {"uid": uid})

async def use_heartbeat_api(uid):
    return await api_post("/api/use_heartbeat", {"uid": uid})

async def buy_heartbeats_api(uid, quantity):
    return await api_post("/api/buy_heartbeats", {"uid": uid, "quantity": quantity})

async def buy_gems_api(uid, quantity):
    return await api_post("/api/buy_gems", {"uid": uid, "quantity": quantity})

async def buy_subscription_api(uid, quantity):
    return await api_post("/api/buy_subscription", {"uid": uid, "quantity": quantity})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    await get_user_api(uid)

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

async def mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    scenario_map = {
        "mood_whispering": "Step into a world of gentle whispers and magical dreams.",
        "mood_night": "A mysterious night awaits—romance under the moonlight.",
        "mood_forest": "You meet a mysterious stranger deep in an enchanted forest.",
        "mood_roommate": "Your seductive roommate is full of playful charm.",
        "mood_dreamy": "Experience a love that's dreamy, soft, and surreal.",
        "mood_fiery": "Passion burns hot—are you ready for a bold encounter?",
        "mood_enchanted": "An encounter with a magical being in a fairy-tale world.",
        "mood_candlelit": "A candlelit room sets the mood for mystery and romance."
    }
    mood_choice = mood_map.get(query.data, "💫 Whispering Fantasy")
    scenario = scenario_map.get(query.data, "")

    user_data[uid] = user_data.get(uid, {})
    user_data[uid]["mood"] = mood_choice

    await query.edit_message_text(
        f"Mood set to: {mood_choice}!\n\n{scenario}\n\nNow type anything and let's chat ❤️"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = await get_user_api(uid)
    await update.message.reply_text(
        f"**Your Profile**\n"
        f"Name: {update.effective_user.first_name or 'Unknown'}\n"
        f"Heartbeats: {data.get('heartbeats', 0)}\n"
        f"Gems: {data.get('gems', 0)}\n"
        f"Subscription Expiry: {data.get('subscription_expiry', '--/--/----')}"
    )

async def forgetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Optional: Implement a delete user API in your backend if needed.
    await update.message.reply_text("Memory wiped... but I’ll miss our chats 💔")

async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    try:
        user_info = await get_user_api(uid)
        current = int(user_info.get("heartbeats", 0))
        to_add = max(5 - current, 0)
        if to_add > 0:
            await buy_heartbeats_api(uid, to_add)
        await update.message.reply_text("Your heartbeats have been reset! ❤️")
    except Exception as e:
        logging.error(f"Error in resetme: {e}")
        await update.message.reply_text("Failed to reset heartbeats. Please try again.")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram user ID is: {update.effective_user.id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    result = await use_heartbeat_api(uid)

    # Admin auto-reset logic, with NO early return
    if update.effective_user.id == ADMIN_USER_ID and (result.get("heartbeats", 0) <= 0):
        await buy_heartbeats_api(uid, 5)
        await update.message.reply_text("Admin detected! Your heartbeats have been automatically reset.")
        # Re-fetch heartbeats after resetting to continue as normal
        result = await get_user_api(uid)
        # Don't return! Allow the rest of the function to run

    if not result.get("success", True) or result.get("heartbeats", 0) <= 0:
        await update.message.reply_text(
            "You're out of heartbeats! Invite a friend or buy more to continue.\n\nIf you are the admin, use /resetme to restore your heartbeats."
        )
        return

    await send_typing_action(update, context)

    try:
        user_input = update.message.text
        logging.info(f"User Input from {uid}: {user_input}")

        user_api_data = await get_user_api(uid)
        reply = await generate_reply(uid, user_input, user_data.get(uid, {}))
        logging.info(f"Generated Reply: {reply}")

        if not reply or reply.strip() == "":
            raise ValueError("Generated reply is empty or invalid.")

        await update.message.reply_text(reply)

        if user_data.get(uid, {}).get("fantasy_mode"):
            image = get_random_fantasy_image()
            if image:
                logging.info(f"Fantasy Image URL: {image}")
                await update.message.reply_photo(photo=image)
            else:
                logging.warning(f"No fantasy image returned for user {uid}.")

        logging.info(
            f"User {uid} heartbeat decremented via API. Remaining heartbeats: {result.get('heartbeats', 0)}"
        )

    except ValueError as ve:
        logging.warning(f"ValueError in handle_message for user {uid}: {ve}")
        await update.message.reply_text("Sorry, I couldn't process your input. Please try again!")
    except Exception as e:
        logging.error(f"Error in handle_message for user {uid}: {e}", exc_info=True)
        await update.message.reply_text("Oops! Something went wrong. Try again later 💖")

def run():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("forgetme", forgetme))
    application.add_handler(CommandHandler("resetme", resetme))
    application.add_handler(CommandHandler("myid", myid))
    application.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()

if __name__ == "__main__":
    run()