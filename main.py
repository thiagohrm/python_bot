"""
Telegram QR Code Bot - Main Application Entry Point (Redirect)

This is a lightweight entry point that delegates to the modular structure in src/.
All actual bot logic is located in src/main.py for clean organization.
"""

from src.main import main

if __name__ == '__main__':
    main()
