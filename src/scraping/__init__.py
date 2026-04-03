"""Scraping module for web content extraction."""

from src.scraping.web_scraping import is_url, fetch_webpage_title, fetch_webpage_title_from_html

__all__ = [
    'is_url',
    'fetch_webpage_title',
    'fetch_webpage_title_from_html',
]
