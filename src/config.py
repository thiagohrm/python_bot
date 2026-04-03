"""
Configuration and constants for the Telegram QR Code Bot.
"""

import os
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Logger
logger = logging.getLogger(__name__)

# Bot configuration - lazy loading to avoid import-time errors
def get_token():
    """Get the Telegram bot token from environment variables."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")
    return token

# HTTP headers for web requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Default table and div IDs
DEFAULT_TABLE_ID = "tabResult"
DEFAULT_DIV_ID = "conteudo"

# DataFrame column structure
EXPECTED_COLUMNS = ['Produto', 'Código', 'Qtde', 'UN', 'Vl_Unit', 'Vl_Total']

# Request timeout
REQUEST_TIMEOUT = 5
