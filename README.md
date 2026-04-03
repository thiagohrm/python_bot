# python_bot

A Telegram bot that decodes QR codes from images.

## Setup

### System Dependencies
The bot requires the `zbar` shared library for QR code detection:

**Linux/Ubuntu:**
```bash
sudo apt-get install libzbar0
```

**macOS:**
```bash
brew install zbar
```

**Windows:**
`pyzbar` includes the necessary binaries automatically.

### Python Dependencies
1. Install Python dependencies:
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

Note: The Dockerfile handles system dependencies automatically.

## CI/CD Testing

For CI/CD pipelines (GitHub Actions, GitLab CI, etc.), add system dependencies:

**GitHub Actions example:**
```yaml
- name: Install system dependencies
  run: sudo apt-get install -y libzbar0

- name: Install Python dependencies
  run: pip install -r requirements.txt

- name: Run tests
  run: pytest -v
```

Note: Tests automatically mock `pyzbar` during test collection to work in environments without system libraries.

## Usage

- Start a chat with your bot on Telegram.
- Send `/start` to get started.
- Send an image containing a QR code, and the bot will reply with the decoded text.