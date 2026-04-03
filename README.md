# python_bot

A modular Telegram bot that decodes QR codes from images and automatically extracts webpage content from URL-based QR codes. Built with clean architecture principles for maintainability and extensibility.

## Features

- 📱 **QR Code Detection**: Scans images and detects QR codes
- 🔗 **URL Detection**: Automatically identifies if QR code contains a URL
- 🌐 **Webpage Scraping**: Fetches and extracts title, description, and content from detected URLs
- 📊 **Div Data Extraction**: Extracts structured data from HTML div elements (company info, CNPJ, addresses, etc.)
- 📋 **Table Data Extraction**: Extracts product/inventory data from HTML tables and creates pandas DataFrames
- 💾 **DataFrame Storage**: Stores extracted table data as pandas DataFrames for later analysis
- ⚠️ **Error Handling**: Gracefully handles network errors, timeouts, and invalid URLs
- 🏗️ **Modular Architecture**: Clean separation of concerns with dedicated modules for each functionality
- ✅ **Comprehensive Tests**: 20 test cases covering all modules and edge cases

## Architecture

This project follows a modular architecture that separates concerns into dedicated modules:

- **`config.py`**: Centralized configuration management
- **`data_extraction.py`**: HTML parsing and structured data extraction
- **`data_processing.py`**: Data manipulation and DataFrame operations
- **`web_scraping.py`**: HTTP requests and webpage content processing
- **`bot_handlers.py`**: Telegram bot interaction logic
- **`main.py`**: Application entry point and orchestration

This design enables:
- **Independent testing** of each module
- **Easy maintenance** and code reuse
- **Clear separation of concerns**
- **Scalable development** with focused responsibilities

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
pylint *.py
```

Configuration files:
- `.flake8` - Flake8 configuration
- `.pylintrc` - Pylint configuration

### Local Testing
```bash
# Run all tests
pytest -v

# Run tests with coverage
pytest --cov --cov-report=html

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
   - Pytest: Unit tests across all modules
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

### Basic QR Code Scanning
1. Start a chat with your bot on Telegram
2. Send `/start` to get instructions
3. Send an image containing a QR code
4. The bot will decode and reply with the content

### URL Detection and Webpage Scraping
If the QR code contains a URL, the bot will:
1. ✅ Detect it's a URL
2. 🌐 Fetch the webpage
3. 📄 Extract and return:
   - Page title
   - Meta description
   - First paragraph text
   - **Structured data from HTML div elements** (company info, CNPJ, addresses, etc.)

**Example:**
```
User: [Sends image with QR code pointing to https://example.com]
Bot: 🔗 QR Code URL found: https://example.com
     ⏳ Fetching webpage...
     📄 Title: Example Domain
     📝 Description: Example Domain. This domain is for use...
     Example text from article...
     🏢 Company: GERALDO BENEDETE COMPANHIA LTDA
     📋 CNPJ: 45.477.452/0001-05
     📍 AVENIDA GETULIO VARGAS, 339, BAMBU, PORTO FELIZ, SP
```

The bot automatically attempts to extract structured data from div elements when fetching URL-based QR codes.

### Table Data Extraction & DataFrames
The bot can extract product/inventory data from HTML tables and store it as pandas DataFrames for analysis.

**Supported table structure:**
- Product name (span class="txtTit")
- Product code (span class="RCod")
- Quantity (span class="Rqtd")
- Unit (span class="RUN")
- Unit price (span class="RvlUnit")
- Total value (span class="valor")

**Example table extraction:**
```
📊 Products Found: 1

1. CREME LEITE NESTLE TP 200G
   📋 Code: 12332
   🔢 Qty: 1
   📦 Unit: UN0001
   💰 Unit Price: R$ 5.79
   💵 Total: R$ 5.79

💾 Products data stored! Use /dataframe to view it.
```

**DataFrame Access:**
Use `/dataframe` command to view stored product data with totals and summaries.

### Error Handling
The bot handles various error scenarios:
- 🔴 Connection errors
- ⏱️ Request timeouts  
- 🚫 Invalid URLs
- 📵 No QR code found in image

## API Reference

### `extract_div_data(html_content, div_id="conteudo")`
Extracts structured data from a specific HTML div element.

**Parameters:**
- `html_content` (str): The HTML content to parse
- `div_id` (str): The ID of the div element to extract (default: "conteudo")

**Returns:**
- str: Formatted data with emoji icons, or error message if div not found

**Example:**
```python
from data_extraction import extract_div_data
# 📋 CNPJ: 99.999.999/0001-00
# 📍 RUA PRINCIPAL, 1000, SAO PAULO, SP
```

### `is_url(text)`
Validates if text is a valid URL.

**Parameters:**
- `text` (str): The text to validate

**Returns:**
- bool: True if valid URL, False otherwise

**Example:**
```python
from web_scraping import is_url

print(is_url("https://example.com"))  # True
print(is_url("not a url"))            # False
```

### `fetch_webpage_title(url)`
Fetches a URL and extracts page metadata and div data.

**Parameters:**
- `url` (str): The URL to fetch

**Returns:**
- str: Formatted webpage content including title, description, content, and extracted div data (if present)

**Example:**
```python
import asyncio
from web_scraping import fetch_webpage_title

async def main():
    result = await fetch_webpage_title("https://example.com")
    print(result)

asyncio.run(main())
```

## Project Structure

```
python_bot/
├── main.py                          # Application entry point
├── config.py                        # Configuration constants and settings
├── data_extraction.py               # HTML parsing and data extraction utilities
├── data_processing.py               # DataFrame creation and formatting
├── web_scraping.py                  # HTTP requests and webpage content extraction
├── bot_handlers.py                  # Telegram bot command and message handlers
├── __init__.py                      # Package initialization
├── tests/
│   ├── test_main.py                # Comprehensive unit tests (20 tests)
│   └── conftest.py                 # Pytest configuration and mocking
├── .github/
│   └── workflows/
│       └── ci-cd.yml               # GitHub Actions pipeline
├── Dockerfile                       # Container configuration
├── docker-compose.yml              # Docker Compose orchestration
├── requirements.txt                # Python dependencies
├── README.md                        # This file
├── example_extract_div.py          # Example usage of div extraction
└── example_extract_table.py        # Example usage of table extraction
```

## Key Functions

**config.py:**
- Configuration constants (TOKEN, DEFAULT_HEADERS, REQUEST_TIMEOUT, etc.)

**data_extraction.py:**
- `extract_div_data(html_content, div_id)` - HTML div data extraction
- `extract_table_data(html_content, table_id)` - HTML table data extraction

**data_processing.py:**
- `create_products_dataframe(table_data)` - Create pandas DataFrame from table data
- `format_dataframe_for_display(df)` - Format DataFrame for Telegram display

**web_scraping.py:**
- `is_url(text)` - URL validation
- `fetch_webpage_title(url)` - Async webpage fetching and parsing
- `fetch_webpage_title_from_html(html_content)` - Extract data from HTML content

**bot_handlers.py:**
- `start()` - Bot command handler for `/start`
- `get_dataframe()` - Display stored products DataFrame
- `handle_photo(update, context)` - Main QR code detection handler

**main.py:**
- `main()` - Application entry point

## Testing

The project includes comprehensive automated tests:

**Test Coverage:**
- ✅ 20 unit tests
- ✅ All tests passing
- ✅ Async handler testing
- ✅ Edge case handling (missing divs, invalid URLs, network errors)
- ✅ BeautifulSoup parsing validation
- ✅ Table data extraction and DataFrame creation

**Test Categories:**
- QR code detection and decoding
- URL validation
- Webpage scraping and parsing
- HTML div data extraction
- Error handling and recovery

Run tests locally:
```bash
pytest -v --cov --cov-report=term-missing
```

## Examples

### Example 1: HTML Div Extraction
See [example_extract_div.py](example_extract_div.py) for full usage examples.

```python
from data_extraction import extract_div_data

html = """
<div id="conteudo">
  <div class="txtTopo">COMPANY NAME</div>
  <div class="text">CNPJ: XX.XXX.XXX/0001-XX</div>
  <div class="text">RUA STREET, 123, CITY, STATE</div>
</div>
"""

result = extract_div_data(html)
print(result)
```

### Example 2: QR Code in Bot
1. Start bot: `/start`
2. Send image with QR code
3. Bot automatically:
   - Detects QR code
   - Extracts URL if present
   - Fetches webpage
   - Extracts company information and displays formatted data

## Dependencies

### Core
- `python-telegram-bot` - Telegram bot framework
- `pyzbar` - QR code detection library
- `Pillow` - Image processing

### Web Scraping
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation and DataFrame creation

### Development
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `flake8` - Style guide enforcement
- `pylint` - Code analysis

See `requirements.txt` for exact versions.

## Troubleshooting

### QR Code not detected
- Ensure image quality is good
- Try different angles/lighting
- Check that QR code is fully visible

### Webpage scraping fails
- Verify URL in QR code is accessible
- Check internet connection
- Some websites may have access restrictions

### Div extraction returns error
- Verify div ID matches page structure
- Check that HTML contains expected class names
- Some pages may have different structures

## License

This project is open source and available under the MIT License.