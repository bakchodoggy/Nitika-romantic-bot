import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("Hello! The bot is running.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # Add your other handlers here
    app.run_polling()

if __name__ == "__main__":
    main()