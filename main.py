"""
Telegram QR Code Bot - Main Application Entry Point

This is the new entry point. The actual bot logic is in src/main.py

A modular Telegram bot that decodes QR codes from images and extracts
structured data from web pages including company information and product tables.
"""

from src.main import main  # noqa: F401

if __name__ == '__main__':
    main()

