# python_bot

A modular Telegram bot that decodes QR codes from images and extracts structured data from URL-based QR pages.

## Features

- QR code detection from Telegram image uploads
- NFC-e URL validation (Sefaz/SEFAZ hostnames)
- HTML data extraction:
  - company name and CNPJ
  - product table extraction
  - payment summary extraction
  - emission/protocol info and access key (chave de acesso)
- Persistent data storage:
  - `data/scans.csv` — summary index (ID, Date, Company, CNPJ, Amount, Method, Access Key)
  - `data/scans.json` — full scan records including all line items
- Bot commands: `/help`, `/last`, `/scans`, `/detail <id>`
- Modular codebase under `src/` for maintainability
- Automated tests with pytest (43 tests)

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
|   |-- data/
|   |   |-- __init__.py
|   |   `-- store.py
|   |-- extraction/
|   |   |-- __init__.py
|   |   |-- data_extraction.py
|   |   `-- data_processing.py
|   `-- scraping/
|       |-- __init__.py
|       `-- web_scraping.py
|-- data/
|   |-- scans.csv
|   `-- scans.json
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

- `src/config.py`: constants, logger, and environment token lookup
- `src/bot/handlers.py`: Telegram command/photo handlers (`/start`, `/help`, `/last`, `/scans`, `/detail`)
- `src/data/store.py`: CSV and JSON read/write logic, scan ID generation, detail lookup
- `src/scraping/web_scraping.py`: Sefaz URL validation (`is_sefaz_url`) + webpage fetch
- `src/extraction/data_extraction.py`: HTML parsing for company info, table, totals, emission, and access key
- `src/extraction/data_processing.py`: product table formatting
- `src/main.py`: bot bootstrap and handler registration
- `main.py`: lightweight compatibility entrypoint that delegates to `src.main`

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message, points to `/help` |
| `/help` | Lists all available commands |
| `/last` | Shows the last scanned NFC-e summary from CSV |
| `/scans` | Lists all scans as a formatted table |
| `/detail <id>` | Shows the full receipt for the given scan ID (items, totals, dates) |

Send a photo containing an NFC-e QR code to trigger a scan. The bot replies with a one-line summary on success or one of the following errors:

- `No QR Code Found.`
- `No Sefaz link found.`
- `Sefaz site is down.`
- `Data bad formatted.`

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
- Container runs python -m src.main

## Testing

Run tests:

```bash
pytest -v
```

With coverage:

```bash
pytest --cov --cov-report=term-missing
```

## Import Examples

```python
from src.extraction.data_extraction import extract_div_data, extract_table_data, extract_company_info, extract_emission_info
from src.extraction.data_processing import create_products_dataframe
from src.scraping.web_scraping import is_sefaz_url, fetch_webpage
from src.data.store import save_scan_to_csv, save_scan_to_json, get_last_scan_from_csv, get_all_scans_from_csv, get_scan_detail_from_json, next_scan_id
from src.bot.handlers import handle_photo, last_scan, list_scans, detail_scan
```

## Troubleshooting

- Bot exits on startup: ensure TELEGRAM_BOT_TOKEN is set.
- QR decode issues in Linux containers: confirm libzbar0 is installed (already handled in Dockerfile).
- URL fetch failures: verify outbound network access and URL validity.
