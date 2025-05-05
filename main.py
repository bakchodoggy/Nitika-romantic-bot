import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from chat_manager import generate_reply
from data_manager import load_user, save_user
from fantasy_manager import get_random_fantasy_image
from payment_manager import handle_payment
from utils import send_typing_action, trim_reply

TOKEN = "your_telegram_bot_token"

app = ApplicationBuilder().token(TOKEN).build()

user_data = {}

@app.command_handler()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user_data[uid] = load_user(uid)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey handsome, I’m Nitika... your dreamy companion. Type anything and let's get flirty.")

@app.command_handler()
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = user_data.get(uid) or load_user(uid)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Profile:\nName: {data.get('name', 'Unknown')}\nHeartbeats: {data.get('heartbeats', 0)}")

@app.command_handler()
async def forgetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    save_user(uid, {})
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Memory wiped... but I’ll miss our chats.")

@app.message_handler(filters.TEXT & ~filters.COMMAND)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user_data.setdefault(uid, load_user(uid))

    data = user_data[uid]
    if data.get("heartbeats", 5) <= 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You're out of heartbeats! Invite a friend or buy more to continue.")
        return

    await send_typing_action(update, context)

    user_input = update.message.text
    reply = await generate_reply(uid, user_input, data)
    reply = trim_reply(reply)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

    if data.get("fantasy_mode") == True:
        image = get_random_fantasy_image()
        if image:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)

    data["heartbeats"] = data.get("heartbeats", 5) - 1
    save_user(uid, data)

if __name__ == "__main__":
    asyncio.run(app.run_polling())
