# Terminal Stock Chart Application

A terminal-based application for viewing stock charts and information using Yahoo Finance data.

## Features

- Real-time stock data fetching from Yahoo Finance
- Line and candlestick chart visualization in the terminal
- Detailed stock information display
- Interactive keyboard controls
- Customizable time periods and intervals
- Clean and intuitive terminal interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pystock
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

### Controls

- Enter a ticker symbol (e.g., AAPL, MSFT, GOOGL) to view stock data
- Press 's' to search for a new ticker
- Press 'c' to change the time interval
- Press Enter to return to the main menu
- Type 'exit' in the main menu to quit

### Time Periods

- 1 Day
- 5 Days
- 1 Month
- 3 Months
- 6 Months (default)
- 1 Year
- 5 Years

### Chart Types

- Line Chart (default)
- Candlestick Chart

## Dependencies

- yfinance: Yahoo Finance market data downloader
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- plotext: Terminal plotting library

## License

MIT License 