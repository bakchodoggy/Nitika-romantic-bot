import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackContext
)
from chat_manager import generate_reply
from data_manager import load_user, save_user
from fantasy_manager import get_random_fantasy_image
from payment_manager import handle_payment
from utils import send_typing_action, trim_reply

TOKEN = "your_telegram_bot_token"

app = ApplicationBuilder().token(TOKEN).build()
user_data = {}

async def start(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    user_data[uid] = load_user(uid)
    await update.message.reply_text("Hey handsome, I’m Nitika... your dreamy companion. Type anything and let's get flirty.")

async def profile(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid)
    await update.message.reply_text(f"Profile:\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}")

async def forgetme(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    save_user(uid, {})
    await update.message.reply_text("Memory wiped... but I’ll miss our chats.")

async def handle_message(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    user_data.setdefault(uid, load_user(uid))

    data = user_data[uid]
    if data.get("heartbeats", 5) <= 0:
        await update.message.reply_text("You're out of heartbeats! Invite a friend or buy more to continue.")
        return

    await send_typing_action(update, context)

    user_input = update.message.text
    reply = await generate_reply(uid, user_input, data)
    reply = trim_reply(reply)

    await update.message.reply_text(reply)

    if data.get("fantasy_mode") == True:
        image = get_random_fantasy_image()
        if image:
            await update.message.reply_photo(photo=image)

    data["heartbeats"] = data.get("heartbeats", 5) - 1
    save_user(uid, data)

# Adding Handlers to the Application
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("forgetme", forgetme))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()