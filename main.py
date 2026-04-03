import os
import logging
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me an image with a QR code, and I\'ll try to decode it.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages."""
    # Get the photo file
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)

    # Download the photo
    photo_bytes = await file.download_as_bytearray()
    image = Image.open(BytesIO(photo_bytes))

    # Decode QR codes
    decoded_objects = decode(image)

    if decoded_objects:
        # Send back the decoded data
        for obj in decoded_objects:
            await update.message.reply_text(f"QR Code found: {obj.data.decode('utf-8')}")
    else:
        await update.message.reply_text("No QR code found in the image.")

def main():
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
