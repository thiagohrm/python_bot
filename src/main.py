"""
Telegram QR Code Bot - Main Application Entry Point

A modular Telegram bot that decodes QR codes from images and extracts
structured data from web pages including company information and product tables.
"""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.config import get_token
from src.bot.handlers import start, get_dataframe, handle_photo


def main():
    """Start the bot."""
    application = ApplicationBuilder().token(get_token()).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dataframe", get_dataframe))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
