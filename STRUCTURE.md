# Project Structure Guide

## New Modular Organization

The project has been reorganized into a clean, maintainable folder structure:

```
python_bot/
├── src/                          # Main application source code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration constants
│   ├── main.py                  # Application entry point
│   │
│   ├── extraction/              # Data extraction module
│   │   ├── __init__.py
│   │   ├── data_extraction.py   # HTML parsing (div, table extraction)
│   │   └── data_processing.py   # DataFrame operations
│   │
│   ├── scraping/                # Web scraping module
│   │   ├── __init__.py
│   │   └── web_scraping.py      # HTTP requests, webpage content
│   │
│   └── bot/                     # Telegram bot module
│       ├── __init__.py
│       └── handlers.py          # Bot command and message handlers
│
├── tests/                       # Test suite
│   ├── test_main.py            # All unit tests
│   └── conftest.py             # Pytest configuration
│
├── .github/                     # GitHub configuration
│   └── workflows/
│       └── ci-cd.yml           # CI/CD pipeline
│
├── main.py                      # Root entry point (redirects to src/main.py)
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── STRUCTURE.md                 # This file - Architecture guide
├── PR_DATA_EXTRACTION.md        # Pull request template
├── Dockerfile                   # Container configuration
└── docker-compose.yml          # Docker compose orchestration
```

## Module Organization

### `src/`: Source Code

#### `config.py`
- Centralized configuration management
- Environment variable handling (tokens, API keys)
- Default constants (headers, timeouts, IDs)
- Logging configuration

#### `extraction/`: Data Extraction Module
- **`data_extraction.py`**: HTML parsing utilities
  - `extract_div_data()` - Extract structured data from HTML divs
  - `extract_table_data()` - Extract table rows as dictionaries
  
- **`data_processing.py`**: DataFrame operations
  - `create_products_dataframe()` - Create pandas DataFrames from extracted data
  - `format_dataframe_for_display()` - Format data for Telegram display

#### `scraping/`: Web Scraping Module
- **`web_scraping.py`**: HTTP utilities
  - `is_url()` - URL validation
  - `fetch_webpage_title()` - Async webpage fetching
  - `fetch_webpage_title_from_html()` - Parse HTML content

#### `bot/`: Telegram Bot Module
- **`handlers.py`**: Bot interaction handlers
  - `start()` - /start command handler
  - `get_dataframe()` - /dataframe command handler
  - `handle_photo()` - Image processing handler

#### `main.py`
- Application entry point
- Bot initialization
- Handler registration
- Polling setup

### `tests/`: Test Suite
- Comprehensive unit tests covering all modules
- Async handler testing
- Mock-based isolation testing
- 20 passing tests

## Benefits of This Structure

✅ **Clear Organization** - Related functionality grouped logically
✅ **Easy Navigation** - Fast to find specific features
✅ **Scalability** - Simple to add new modules
✅ **Maintainability** - Reduced cognitive load
✅ **Testability** - Isolated modules are easier to test
✅ **Reusability** - Modules can be imported independently
✅ **Documentation** - Clear structure aids understanding

## Import Patterns

### Within the project:
```python
# From src/main.py - importing from extraction module
from src.extraction import extract_div_data, create_products_dataframe

# From src/bot/handlers.py - importing from scraping
from src.scraping import is_url, fetch_webpage_title_from_html

# From examples/extract_div.py - importing extraction functions
from src.extraction import extract_div_data
```

### Running the Application

```bash
# From root directory
python main.py

# Alternatively
python src/main.py
```

## Running Tests

```bash
# From root directory
pytest tests/test_main.py -v

# With coverage
pytest tests/test_main.py --cov=src --cov-report=html
```

## Adding New Modules

To add new functionality:

1. **If it's data extraction logic**: Add to `src/extraction/`
2. **If it's web scraping logic**: Add to `src/scraping/`
3. **If it's bot handling logic**: Add to `src/bot/`
4. **If it's a new feature area**: Create new directory under `src/`

Example structure for a new `analytics` module:
```
src/analytics/
├── __init__.py
├── stats.py
└── reporting.py
```

## Migration Notes

- Root-level `config.py`, `data_extraction.py`, etc. are kept for backward compatibility
- All logic implemented in `src/` folder
- Root `main.py` redirects to `src/main.py`
- Tests import from `src/` directly

## Continuous Integration

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:
- Runs linting (Flake8, Pylint)
- Executes all tests
- Generates coverage reports
- Tests on multiple Python versions

All checks pass with the new modular structure! ✅
