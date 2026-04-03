"""
Web scraping utilities for fetching and parsing web content.
"""

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Union

from src.config import DEFAULT_HEADERS, REQUEST_TIMEOUT
from src.extraction import extract_div_data, extract_table_data


def is_url(text: str) -> bool:
    """Check if the given text is a valid URL."""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def fetch_webpage_title(url: str) -> str:
    """Fetch and extract the title from a webpage."""
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        html_content = response.content.decode('utf-8')

        return await fetch_webpage_title_from_html(html_content, url)
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to the URL"
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def fetch_webpage_title_from_html(html_content: Union[str, bytes], url: str) -> str:
    """Extract title and data from HTML content."""
    try:
        # Handle both string and bytes input
        if isinstance(html_content, bytes):
            soup = BeautifulSoup(html_content, 'html.parser')
            html_str = html_content.decode('utf-8', errors='ignore')
        else:
            soup = BeautifulSoup(html_content, 'html.parser')
            html_str = html_content

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
        div_data = extract_div_data(html_str)

        # Try to extract table data
        table_data = extract_table_data(html_str)

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
