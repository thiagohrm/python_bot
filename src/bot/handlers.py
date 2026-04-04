"""
Telegram bot handlers for processing commands and messages.
"""

import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from src.config import DEFAULT_HEADERS, REQUEST_TIMEOUT
from src.scraping.web_scraping import is_url, is_sefaz_url
from src.extraction.data_extraction import (
    extract_company_info,
    extract_table_data,
    extract_total_data,
    extract_emission_info,
)
from src.data.store import (
    save_scan_to_csv,
    save_scan_to_json,
    get_last_scan_from_csv,
    get_all_scans_from_csv,
    get_scan_detail_from_json,
    next_scan_id,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a photo with a Nota Fiscal QR code.\n"
        "Use /help to see all available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the list of available commands."""
    await update.message.reply_text(
        "Available commands:\n"
        "  /start \u2014 welcome message\n"
        "  /help \u2014 show this help\n"
        "  /last \u2014 show last scanned receipt summary\n"
        "  /scans \u2014 list all recorded scans as a table\n"
        "  /detail <id> \u2014 show full detail for a scan by its ID\n\n"
        "Send a photo containing a Nota Fiscal QR code to scan it."
    )


async def last_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return the last scanned receipt summary from stored CSV data."""
    row = get_last_scan_from_csv()
    if not row:
        await update.message.reply_text("No scans recorded yet. Send a QR code image first!")
        return
    msg = (
        "Last scanned receipt:\n"
        f"Date: {row.get('Date', 'N/A')}\n"
        f"Company: {row.get('Company Name', 'N/A')}\n"
        f"CNPJ: {row.get('CNPJ', 'N/A')}\n"
        f"Amount Paid: R$ {row.get('Amount Paid', 'N/A')}\n"
        f"Payment Method: {row.get('Payment Method', 'N/A')}"
    )
    await update.message.reply_text(msg)


async def list_scans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return all recorded scans as a monospace table."""
    rows = get_all_scans_from_csv()
    if not rows:
        await update.message.reply_text("No scans recorded yet. Send a QR code image first!")
        return

    # Fixed column widths for the table
    id_w, date_w, company_w, amount_w, method_w = 4, 19, 20, 10, 12
    header = (
        f"{'ID':<{id_w}} {'Date':<{date_w}} {'Company':<{company_w}} {'Amount':>{amount_w}} {'Method':<{method_w}}"
    )
    separator = "-" * len(header)
    lines = [header, separator]
    for row in rows:
        rid = row.get("ID", "")[:id_w]
        date = row.get("Date", "")[:date_w]
        company = row.get("Company Name", "")[:company_w]
        amount = row.get("Amount Paid", "")[:amount_w]
        method = row.get("Payment Method", "")[:method_w]
        lines.append(
            f"{rid:<{id_w}} {date:<{date_w}} {company:<{company_w}} {amount:>{amount_w}} {method:<{method_w}}"
        )

    table = "\n".join(lines)
    # Telegram monospace block limit is 4096 chars; truncate if needed
    if len(table) > 3900:
        table = table[:3900] + "\n... (truncated)"
    await update.message.reply_text(f"```\n{table}\n```", parse_mode="MarkdownV2")


async def detail_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return full JSON detail for a scan by its ID (usage: /detail <id>)."""
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("Usage: /detail <id>  (e.g. /detail 3)")
        return

    scan_id = int(args[0])
    record = get_scan_detail_from_json(scan_id)
    if not record:
        await update.message.reply_text(f"No scan found with ID {scan_id}.")
        return

    items = record.get("items", [])
    items_text = ""
    for i, item in enumerate(items, start=1):
        items_text += (
            f"  {i}. {item.get('Produto', 'N/A')}\n"
            f"     Code: {item.get('Código', 'N/A')} | "
            f"Qty: {item.get('Qtde', 'N/A')} | "
            f"Unit: {item.get('UN', 'N/A')}\n"
            f"     Price: R$ {item.get('Vl_Unit', 0):.2f} | "
            f"Total: R$ {item.get('Vl_Total', 0):.2f}\n"
        )

    msg = (
        f"Scan #{record.get('id')}\n"
        f"Date: {record.get('emission_date', 'N/A')}\n"
        f"Company: {record.get('company_name', 'N/A')}\n"
        f"CNPJ: {record.get('cnpj', 'N/A')}\n"
        f"Access Key: {record.get('access_key', 'N/A')}\n"
        f"Items ({record.get('total_items', len(items))}):\n{items_text}"
        f"Amount Paid: R$ {record.get('amount_paid', 0):.2f}\n"
        f"Payment: {record.get('payment_method', 'N/A')}"
    )
    await update.message.reply_text(msg)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages and process NFC-e QR codes."""
    try:
        from io import BytesIO
        from PIL import Image
        from pyzbar.pyzbar import decode

        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(BytesIO(photo_bytes))
        decoded_objects = decode(image)

        if not decoded_objects:
            await update.message.reply_text("No QR Code Found.")
            return

        qr_data = decoded_objects[0].data.decode('utf-8')

        if not is_url(qr_data) or not is_sefaz_url(qr_data):
            await update.message.reply_text("No Sefaz link found.")
            return

        try:
            response = requests.get(qr_data, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            await update.message.reply_text("Sefaz site is down.")
            return
        except requests.exceptions.ConnectionError:
            await update.message.reply_text("Sefaz site is down.")
            return
        except requests.exceptions.HTTPError:
            await update.message.reply_text("Sefaz site is down.")
            return

        html_content = response.content.decode('utf-8', errors='ignore')

        company_info = extract_company_info(html_content)
        table_data = extract_table_data(html_content)
        total_data = extract_total_data(html_content)
        emission_info = extract_emission_info(html_content)

        if not table_data or not total_data or not emission_info:
            await update.message.reply_text("Data bad formatted.")
            return

        emission_date = emission_info.get('emission_date', '')
        company_name = company_info.get('company_name', '')
        cnpj = company_info.get('cnpj', '')
        amount_paid = total_data.get('amount_paid', total_data.get('amount_to_pay', 0.0))
        payment_method = total_data.get('payment_method', '')
        total_items = total_data.get('total_items', len(table_data))

        scan_id = next_scan_id()
        access_key = emission_info.get('access_key', '')

        save_scan_to_csv(scan_id, emission_date, company_name, cnpj, amount_paid, payment_method, access_key)

        scan_record = {
            "id": scan_id,
            "scan_date": datetime.now().isoformat(),
            "emission_date": emission_date,
            "company_name": company_name,
            "cnpj": cnpj,
            "access_key": access_key,
            "amount_paid": amount_paid,
            "payment_method": payment_method,
            "total_items": total_items,
            "items": table_data,
        }
        save_scan_to_json(scan_record)

        msg = (
            "Receipt scanned successfully!\n"
            f"Date: {emission_date}\n"
            f"Company: {company_name}\n"
            f"Items: {total_items}\n"
            f"Amount Paid: R$ {amount_paid:.2f}\n"
            f"Payment: {payment_method}"
        )
        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Error processing image: {str(e)}")

