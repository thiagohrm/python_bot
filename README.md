# python_bot

A Telegram bot that decodes QR codes from images.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a bot token from [@BotFather](https://t.me/botfather) on Telegram.

3. Set the environment variable:
   ```
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
   On Windows:
   ```
   set TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```
   python main.py
   ```

## Docker

To run with Docker:

1. Set the token in docker-compose.yml:
   ```yaml
   environment:
     - TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

2. Run:
   ```
   docker-compose up --build
   ```

## Usage

- Start a chat with your bot on Telegram.
- Send `/start` to get started.
- Send an image containing a QR code, and the bot will reply with the decoded text.