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
   ```bash
   pip install -r requirements.txt
   ```

2. For development (linting, testing):
   ```bash
   pip install -r requirements-dev.txt
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

## Development

### Linting
Run linters to check code quality:

```bash
# Flake8 (style guide enforcement)
flake8 .

# Pylint (code analysis)
pylint main.py
```

Configuration files:
- `.flake8` - Flake8 configuration
- `.pylintrc` - Pylint configuration

### Local Testing
```bash
# Run all tests
pytest -v

# Run tests with coverage
pytest --cov=main --cov-report=html

# Run specific test
pytest -k "test_start_handler" -v
```

## CI/CD Pipeline

The repository uses GitHub Actions for automated testing and linting.

**Workflow file:** `.github/workflows/ci-cd.yml`

**What runs on each PR:**
1. ✅ **Linting Phase**
   - Flake8: Style guide enforcement
   - Pylint: Code analysis
   
2. 🧪 **Testing Phase**
   - Pytest: Unit tests
   - Coverage: Code coverage analysis
   
3. 📊 **Reporting**
   - Build report comment posted to PR
   - Coverage report generated
   - Lint reports uploaded as artifacts

**Pipeline Status:** The build must pass all checks to merge to main.

**Example PR Comment:**
```
## 📊 CI/CD Build Report

### ✅ Lint Report
...

### 🧪 Test Report
...

### 📈 Status
- Linting: success ✅
- Tests: success ✅
```

## Usage

- Start a chat with your bot on Telegram.
- Send `/start` to get started.
- Send an image containing a QR code, and the bot will reply with the decoded text.