import os
import logging
from io import BytesIO
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
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


def is_url(text: str) -> bool:
    """Check if the given text is a valid URL."""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def fetch_webpage_title(url: str) -> str:
    """Fetch and extract the title from a webpage."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract useful information
        title = soup.title.string if soup.title else 'No title found'

        # Try to get description
        description = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')

        # Get first paragraph
        first_p = soup.find('p')
        first_text = first_p.get_text(strip=True)[:200] if first_p else ''

        # Try to extract structured div data
        div_data = extract_div_data(str(soup))

        # Build response
        result = f"📄 Title: {title}\n\n📝 Description: {description}\n\n{first_text}"

        # Add div data if found (not an error message)
        if not div_data.startswith("❌"):
            result += f"\n\n{div_data}"

        return result
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to the URL"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def extract_div_data(html_content: str, div_id: str = "conteudo") -> str:
    """Extract structured data from specific div elements in HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        target_div = soup.find('div', id=div_id)

        if not target_div:
            return "❌ Error: Target div not found"

        # Extract company name (from txtTopo class)
        company_div = target_div.find('div', class_='txtTopo')
        company_name = company_div.get_text(strip=True) if company_div else 'N/A'

        # Extract all text divs with class 'text'
        text_divs = target_div.find_all('div', class_='text')
        data_lines = []

        for div in text_divs:
            # Clean up text by normalizing whitespace
            text = div.get_text()
            # Replace multiple whitespace characters (including newlines) with single space
            import re
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                data_lines.append(text)

        # Format the result
        result = f"🏢 Company: {company_name}\n\n"
        for i, line in enumerate(data_lines):
            if 'CNPJ' in line:
                result += f"📋 {line}\n"
            elif 'AVENIDA' in line or 'RUA' in line or 'PRACA' in line:
                result += f"📍 {line}\n"
            else:
                result += f"{line}\n"

        return result
    except Exception as e:
        return f"❌ Error extracting div data: {str(e)}"


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
            qr_data = obj.data.decode('utf-8')

            # Check if it's a URL
            if is_url(qr_data):
                msg = f"🔗 QR Code URL found: {qr_data}\n\n⏳ Fetching webpage..."
                await update.message.reply_text(msg)
                webpage_info = await fetch_webpage_title(qr_data)
                await update.message.reply_text(webpage_info)
            else:
                await update.message.reply_text(f"QR Code found: {qr_data}")
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
