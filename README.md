# StockPriceScraper

A real-time stock price monitoring tool that captures NVIDIA (NVDA) stock prices from Google Finance at 5-second intervals. The script uses Selenium for web automation and OCR to extract price data, storing it in a structured CSV format for analysis.

## Features

- Real-time price monitoring every 5 seconds
- Automated web scraping using Selenium WebDriver
- OCR-based price extraction using Tesseract
- Structured data storage in CSV format
- Comprehensive error handling and logging
- Memory-efficient (no permanent screenshot storage)

## Demo

https://github.com/shosseini811/StockPriceScraper/assets/demo.mov

![Demo](demo.mov)

## Data Captured

The script captures and stores the following information:
- Timestamp
- Current stock price
- Price change amount
- Percentage change

## Prerequisites

- Python 3.7 or higher
- Chrome browser
- Tesseract OCR
- macOS (for other operating systems, modifications may be needed)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/StockPriceScraper.git
   cd StockPriceScraper
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Tesseract OCR:
   ```bash
   brew install tesseract
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure Chrome WebDriver:
   - Install ChromeDriver via Homebrew:
     ```bash
     brew install --cask chromedriver
     ```
   - Allow ChromeDriver in System Settings > Privacy & Security

## Usage

1. Start the scraper:
   ```bash
   python stock_scraper.py
   ```

2. The script will:
   - Capture NVIDIA stock price every 5 seconds
   - Extract price information using OCR
   - Save data to `data/nvidia_stock_prices.csv`
   - Log activities to `logs/stock_scraper.log`

3. Stop the script:
   - Press Ctrl+C to gracefully stop the monitoring

## Data Format

The CSV file (`data/nvidia_stock_prices.csv`) contains the following columns:
- `timestamp`: Date and time of capture
- `price`: Current stock price in USD
- `change`: Price change from previous close
- `percent_change`: Percentage change from previous close

## Error Handling

The script includes robust error handling for:
- Network connectivity issues
- Web element loading failures
- OCR extraction errors
- File system operations

All errors are logged to `logs/stock_scraper.log` with timestamps and error details.

## Limitations

- Currently only supports NVIDIA (NVDA) stock
- Requires stable internet connection
- May be affected by Google Finance UI changes
- Rate limited by Google Finance's update frequency

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
