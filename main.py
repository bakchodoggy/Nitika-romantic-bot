import os
import logging
import hmac
import hashlib
import json
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import asyncio

from chat_manager import generate_reply
from data_manager import load_user, save_user
from fantasy_manager import get_random_fantasy_image
from utils import send_typing_action, trim_reply

# ---- CONFIG ----
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_TOKEN is missing! Set it in environment variables.")

ALLOWED_ORIGINS = [
    "https://gems-miniapp-mmf25pgny-sarvesh-beheras-projects.vercel.app",
]

ADMIN_USER_ID = 1444093362

user_data = {}

# ---- FASTAPI APP ----
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- HEALTH CHECK ROUTE ----
@app.get("/")
async def health():
    return {"status": "ok"}

# ---- TELEGRAM HANDLERS ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    user_data[uid] = load_user(uid) or {}
    user_data[uid]["mood"] = mood_choice
    save_user(uid, user_data[uid])

    await query.edit_message_text(
        f"Mood set to: {mood_choice}!\n\n{scenario}\n\nNow type anything and let's chat ❤️"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid) or {}
    await update.message.reply_text(
        f"**Your Profile**\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}\nMood: {data.get('mood', 'Not set')}"
    )

async def forgetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    save_user(uid, {})
    user_data.pop(uid, None)
    await update.message.reply_text("Memory wiped... but I’ll miss our chats 💔")

async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    user_data[uid] = load_user(uid) or {}
    user_data[uid]["heartbeats"] = 5  # or whatever your default is
    save_user(uid, user_data[uid])
    await update.message.reply_text("Your heartbeats have been reset! ❤️")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram user ID is: {update.effective_user.id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "You're out of heartbeats! Invite a friend or buy more to continue.\n\nIf you are the admin, use /resetme to restore your heartbeats."
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

# ---- TELEGRAM MINI APP API ENDPOINT ----
class UserRequest(BaseModel):
    telegram_id: int
    hash: str  # Telegram Mini App's initData

def check_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Validate Telegram Mini App init data."""
    try:
        data = dict(parse_qsl(init_data, strict_parsing=True))
        hash_check = data.pop("hash", None)
        if not hash_check:
            raise ValueError("Missing hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        secret = hashlib.sha256(bot_token.encode()).digest()
        h = hmac.new(secret, data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(h, hash_check):
            raise ValueError("Hash check failed")
        user = json.loads(data["user"])
        return user
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Telegram validation error: {str(e)}")

@app.post("/api/user")
async def get_user_data(req: UserRequest):
    # Validate Telegram
    user = check_telegram_init_data(req.hash, TOKEN)
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Lookup user in your bot's user_data
    uid = str(req.telegram_id)
    data = user_data.get(uid) or load_user(uid) or {}
    return {
        "gems": data.get("gems", 100),
        "heartbeats": data.get("heartbeats", 7),
        "subscription_expires": data.get("subscription_expires", "2025-12-31")
    }

# ---- FASTAPI STARTUP EVENT: start bot ----
@app.on_event("startup")
async def on_startup():
    tg_app = ApplicationBuilder().token(TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("profile", profile))
    tg_app.add_handler(CommandHandler("forgetme", forgetme))
    tg_app.add_handler(CommandHandler("resetme", resetme))
    tg_app.add_handler(CommandHandler("myid", myid))
    tg_app.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    tg_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    asyncio.create_task(tg_app.run_polling())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))