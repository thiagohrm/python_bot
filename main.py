import os
import logging
from io import BytesIO
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
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


async def get_dataframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the stored products DataFrame as formatted text."""
    if 'products_df' in context.user_data and not context.user_data['products_df'].empty:
        df = context.user_data['products_df']
        response = f"📊 Stored Products Data ({len(df)} items):\n\n"

        # Format as a simple table
        for idx, row in df.iterrows():
            response += f"🔹 {row['Produto']}\n"
            response += f"   Code: {row['Código']} | Qty: {row['Qtde']} | Unit: {row['UN']}\n"
            response += f"   Price: R$ {row['Vl_Unit']:.2f} | Total: R$ {row['Vl_Total']:.2f}\n\n"

        # Add summary
        total_value = df['Vl_Total'].sum()
        response += f"💰 Total Value: R$ {total_value:.2f}"

        await update.message.reply_text(response)
    else:
        await update.message.reply_text("No products data stored. Send a QR code image first!")


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
        html_content = response.content

        return await fetch_webpage_title_from_html(html_content, url)
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to the URL"
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def fetch_webpage_title_from_html(html_content: bytes, url: str) -> str:
    """Extract title and data from HTML content."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

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

        # Try to extract table data
        table_data = extract_table_data(str(soup))

        # Build response
        result = f"📄 Title: {title}\n\n📝 Description: {description}\n\n{first_text}"

        # Add div data if found (not an error message)
        if not div_data.startswith("❌"):
            result += f"\n\n{div_data}"

        # Add table data if found
        if table_data:
            result += f"\n\n📊 Products Found: {len(table_data)}\n"
            for i, product in enumerate(table_data, 1):
                result += f"\n{i}. {product.get('Produto', 'N/A')}\n"
                result += f"   📋 Code: {product.get('Código', 'N/A')}\n"
                result += f"   🔢 Qty: {product.get('Qtde', 'N/A')}\n"
                result += f"   📦 Unit: {product.get('UN', 'N/A')}\n"
                result += f"   💰 Unit Price: R$ {product.get('Vl_Unit', '0.00'):.2f}\n"
                result += f"   💵 Total: R$ {product.get('Vl_Total', '0.00'):.2f}\n"

        return result
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


def extract_table_data(html_content: str, table_id: str = "tabResult") -> list:
    """Extract table data and return as list of dictionaries for pandas DataFrame."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', id=table_id)

        if not table:
            return []

        products = []

        # Find all table rows (skip header if exists)
        rows = table.find_all('tr')

        for row in rows:
            # Skip rows that don't contain product data
            if not row.find('span', class_='txtTit'):
                continue

            product_data = {}

            # Extract product name
            name_span = row.find('span', class_='txtTit')
            if name_span:
                product_data['Produto'] = name_span.get_text(strip=True)

            # Extract code
            code_span = row.find('span', class_='RCod')
            if code_span:
                # Extract number from "(Código: 12332 )"
                code_text = code_span.get_text()
                import re
                code_match = re.search(r'Código:\s*(\d+)', code_text)
                product_data['Código'] = code_match.group(1) if code_match else ''

            # Extract quantity
            qty_span = row.find('span', class_='Rqtd')
            if qty_span:
                qty_text = qty_span.get_text()
                qty_match = re.search(r'Qtde\.:\s*(\d+)', qty_text)
                product_data['Qtde'] = int(qty_match.group(1)) if qty_match else 0

            # Extract unit
            unit_span = row.find('span', class_='RUN')
            if unit_span:
                unit_text = unit_span.get_text()
                unit_match = re.search(r'UN:\s*([^\s]+)', unit_text)
                product_data['UN'] = unit_match.group(1) if unit_match else ''

            # Extract unit value
            unit_val_span = row.find('span', class_='RvlUnit')
            if unit_val_span:
                val_text = unit_val_span.get_text()
                val_match = re.search(r'Vl\. Unit\.:\s*([^\s]+)', val_text)
                if val_match:
                    # Convert Brazilian format (5,79) to float (5.79)
                    val_str = val_match.group(1).replace(',', '.')
                    try:
                        product_data['Vl_Unit'] = float(val_str)
                    except ValueError:
                        product_data['Vl_Unit'] = 0.0

            # Extract total value
            total_span = row.find('span', class_='valor')
            if total_span:
                total_text = total_span.get_text(strip=True)
                try:
                    # Convert Brazilian format to float
                    product_data['Vl_Total'] = float(total_text.replace(',', '.'))
                except ValueError:
                    product_data['Vl_Total'] = 0.0

            # Only add if we have at least a product name
            if product_data.get('Produto'):
                products.append(product_data)

        return products
    except Exception as e:
        print(f"Error extracting table data: {str(e)}")
        return []


def create_products_dataframe(table_data: list) -> pd.DataFrame:
    """Create a pandas DataFrame from extracted table data."""
    if not table_data:
        return pd.DataFrame()

    df = pd.DataFrame(table_data)

    # Ensure all expected columns exist
    expected_columns = ['Produto', 'Código', 'Qtde', 'UN', 'Vl_Unit', 'Vl_Total']
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    # Reorder columns
    df = df[expected_columns]

    return df


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

                # Fetch webpage content for both display and data extraction
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(qr_data, headers=headers, timeout=5)
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


def main():
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dataframe", get_dataframe))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
