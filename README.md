# Skin Trader

Automated CS:GO/CS2 skin trading bot that monitors TradeOn.space for profitable deals and automatically purchases skins across multiple marketplaces.

## Features

- **Multi-marketplace support**: CSFloat, CSMoney, and HaloSkins
- **Automated purchasing**: Monitors TradeOn.space console messages and executes purchases automatically
- **Concurrent processing**: Handles multiple purchases simultaneously with configurable concurrency
- **Purchase history tracking**: CSV-based purchase history with duplicate prevention
- **Browser automation**: Uses Playwright/Patchright for reliable web automation
- **Persistent sessions**: Maintains browser profiles and login sessions

## Requirements

- Python 3.13+
- Chrome/Chromium browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd skin-trader-prod
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Install Playwright browsers:
```bash
uv run playwright install chromium
```

4. Configure environment variables:
```bash
cp .env.dist .env
```

Edit `.env` with your settings:
```env
# Browser configuration
BROWSER_HEADLESS=False
BROWSER_USER_DATA_DIR=./browser_data/profiles/
BROWSER_EXTENSION_PATH=./browser_data/extensions/

# Account
ACCOUNT_USERNAME=your_username

# Purchase manager settings
PURCHASE_MANAGER_MAX_CONCURRENT=3
PURCHASE_MANAGER_HISTORY_FILE_PATH=purchases.csv
```

## Usage

Run the bot:
```bash
uv run skin-trader
```

Or using the module directly:
```bash
uv run python -m skin_trader.main
```

## How It Works

1. **Browser Setup**: Launches a persistent browser context with your profile
2. **TradeOn Monitoring**: Opens TradeOn.space and monitors browser console for deal messages
3. **Deal Detection**: Parses console messages to extract item details and marketplace URLs
4. **Purchase Execution**: Automatically navigates to the marketplace and completes the purchase
5. **History Tracking**: Records all purchases to prevent duplicates

## Project Structure

```
src/skin_trader/
├── configs/          # Configuration classes
├── database/         # CSV-based data storage
├── exceptions/       # Custom exceptions
├── factory/          # Factory patterns
├── managers/         # Core business logic
│   ├── browser.py              # Browser automation
│   ├── purchase.py             # Purchase orchestration
│   ├── purchase_history.py    # History tracking
│   ├── purchase_processor.py  # Purchase execution
│   └── purchase_worker.py     # Queue processing
├── markets/          # Marketplace implementations
│   ├── csfloat.py
│   ├── csmoney.py
│   └── haloskins.py
├── parsers/          # Data parsers
│   └── tradeon.py
├── schemas/          # Pydantic models
└── services/         # Service layer
```

## Configuration

### Browser Settings

- `BROWSER_HEADLESS`: Run browser in headless mode (default: False)
- `BROWSER_USER_DATA_DIR`: Directory for browser profiles
- `BROWSER_EXTENSION_PATH`: Directory for browser extensions

### Purchase Manager

- `PURCHASE_MANAGER_MAX_CONCURRENT`: Maximum concurrent purchases (default: 3)
- `PURCHASE_MANAGER_HISTORY_FILE_PATH`: Path to purchase history CSV

## Development

### Code Quality

The project uses:
- **Black**: Code formatting (line length: 160)
- **Ruff**: Linting
- **Basedpyright**: Type checking

Run checks:
```bash
uv run black .
uv run ruff check .
uv run basedpyright
```

## License

This project is for educational purposes only. Use at your own risk.

## Author

uzrama (mark.uzun7@gmail.com)
