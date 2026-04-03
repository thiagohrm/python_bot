"""
Telegram bot handlers for processing commands and messages.
"""

import requests
from telegram import Update
from telegram.ext import ContextTypes

from config import DEFAULT_HEADERS, REQUEST_TIMEOUT
from web_scraping import is_url, fetch_webpage_title_from_html
from data_extraction import extract_table_data
from data_processing import create_products_dataframe, format_dataframe_for_display


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me an image with a QR code, and I\'ll try to decode it.')


async def get_dataframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the stored products DataFrame as formatted text."""
    if 'products_df' in context.user_data and not context.user_data['products_df'].empty:
        df = context.user_data['products_df']
        response = format_dataframe_for_display(df)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("No products data stored. Send a QR code image first!")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages and process QR codes."""
    try:
        # Import here to avoid circular imports
        from io import BytesIO
        from PIL import Image
        from pyzbar.pyzbar import decode

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
                qr_data = obj.data.decode('utf-8')

                # Check if it's a URL
                if is_url(qr_data):
                    msg = f"🔗 QR Code URL found: {qr_data}\n\n⏳ Fetching webpage..."
                    await update.message.reply_text(msg)

                    # Fetch webpage content for both display and data extraction
                    response = requests.get(qr_data, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    html_content = response.content

                    # Extract webpage info for display
                    webpage_info = await fetch_webpage_title_from_html(html_content, qr_data)
                    await update.message.reply_text(webpage_info)

                    # Extract table data and create DataFrame
                    table_data = extract_table_data(str(html_content))
                    if table_data:
                        df = create_products_dataframe(table_data)
                        context.user_data['products_df'] = df
                        await update.message.reply_text("💾 Products data stored! Use /dataframe to view it.")
                else:
                    await update.message.reply_text(f"QR Code found: {qr_data}")
        else:
            await update.message.reply_text("No QR code found in the image.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing image: {str(e)}")