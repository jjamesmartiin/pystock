# import pdb # python debugger; part of stdlib



# basic program structure:

# open the main terminal UI
# it's like vim where it shows a graph of all the stocks in your watchlist called 'default'
# it should have sensible keybinds for adding and removing stocks from the watchlist (using the tickers.txt) 
# it should show a chart of the last 1 year with the candles being every day
# if the user uses ctrl + and ctrl - it should zoom in and out; like to weekly chart with 4h candles, and then WTD chart with hourly candles, then day with 5 min candles

# to add to the watchlist we should basically just open the ticker.txt file in the user's $EDITOR and then reload on save/quit if file changed 


import yfinance as yf
from rich.console import Console
from rich.table import Table

# read lines
with open('tickers.txt', 'r') as file:
    symbols = file.readlines()
symbols = [line.strip().upper() for line in symbols]

# Initialize our console
console = Console()

# Create a table
table = Table(title="Stock Prices")
table.add_column("Symbol", style="cyan")
table.add_column("Price", justify="right")
table.add_column("Change", justify="right")
table.add_column("% Change", justify="right")

# Fetch data for each symbol
for symbol in symbols:
    try:
        # Get stock info
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        # Extract relevant information
        current_price = data.get('currentPrice', 0.0)
        previous_close = data.get('previousClose', 0.0)
        
        # Calculate changes
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close else 0
        
        # Determine color based on change
        change_color = "green" if change >= 0 else "red"
        
        # Add row to table
        table.add_row(
            symbol,
            f"${current_price:.2f}",
            f"[{change_color}]{change:.2f}[/{change_color}]",
            f"[{change_color}]{change_percent:.2f}%[/{change_color}]"
        )
    except Exception as e:
        # Handle any errors
        table.add_row(symbol, "Error", "", "")
        console.print(f"Error fetching {symbol}: {e}")

# Display the table
console.print(table)
