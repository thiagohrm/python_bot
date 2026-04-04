"""
Web scraping module
"""

from src.scraping.web_scraping import (
    is_url,
    is_sefaz_url,
    fetch_webpage_title,
    fetch_webpage_title_from_html
)

__all__ = [
    'is_url',
    'is_sefaz_url',
    'fetch_webpage_title',
    'fetch_webpage_title_from_html'
]
