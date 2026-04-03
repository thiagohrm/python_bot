# python_bot

A modular Telegram bot that decodes QR codes from images and extracts structured data from URL-based QR pages.

## Features

- QR code detection from Telegram image uploads
- URL detection and webpage fetch
- HTML data extraction:
  - company/details block extraction
  - table/products extraction
  - payment summary extraction
  - emission/protocol extraction
- Product DataFrame generation and Telegram-friendly formatting
- Modular codebase under src for maintainability
- Automated tests with pytest

## Project Structure

```text
python_bot/
|-- src/
|   |-- __init__.py
|   |-- config.py
|   |-- main.py
|   |-- bot/
|   |   |-- __init__.py
|   |   `-- handlers.py
|   |-- extraction/
|   |   |-- __init__.py
|   |   |-- data_extraction.py
|   |   `-- data_processing.py
|   `-- scraping/
|       |-- __init__.py
|       `-- web_scraping.py
|-- tests/
|   `-- test_main.py
|-- main.py
|-- requirements.txt
|-- requirements-dev.txt
|-- Dockerfile
|-- docker-compose.yml
`-- .dockerignore
```

## Architecture

- src/config.py: constants, logger, and environment token lookup
- src/bot/handlers.py: Telegram command/photo handlers
- src/scraping/web_scraping.py: URL validation + webpage parsing workflow
- src/extraction/data_extraction.py: HTML parsing helpers for div/table/total/emission
- src/extraction/data_processing.py: DataFrame creation and formatting
- src/main.py: bot bootstrap and handler registration
- main.py: lightweight compatibility entrypoint that delegates to src.main

## Setup

### System dependency

The bot uses pyzbar, which requires zbar shared library on Linux.

Ubuntu/Debian:

```bash
sudo apt-get install libzbar0
```

macOS:

```bash
brew install zbar
```

Windows:

pyzbar usually works with bundled binaries.

### Python dependencies

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

### Telegram token

Set TELEGRAM_BOT_TOKEN environment variable.

Linux/macOS:

```bash
export TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Windows PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN = "your_bot_token_here"
```

## Run

Compatibility entrypoint:

```bash
python main.py
```

Direct modular entrypoint:

```bash
python src/main.py
```

## Docker

Build and run:

```bash
docker-compose up --build
```

Notes:

- Dockerfile installs libzbar0 for QR decoding support
- Container runs python src/main.py

## Testing

Run tests:

```bash
pytest -v
```

With coverage:

```bash
pytest --cov --cov-report=term-missing
```

## Import Examples (new structure)

```python
from src.extraction.data_extraction import extract_div_data, extract_table_data
from src.extraction.data_processing import create_products_dataframe
from src.scraping.web_scraping import is_url, fetch_webpage_title
from src.bot.handlers import handle_photo
```

## Troubleshooting

- Bot exits on startup: ensure TELEGRAM_BOT_TOKEN is set.
- QR decode issues in Linux containers: confirm libzbar0 is installed (already handled in Dockerfile).
- URL fetch failures: verify outbound network access and URL validity.
