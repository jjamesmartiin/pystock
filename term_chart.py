import os
import sys
import termios
import tty
import plotext as plt

def get_key():
    """Get a single keypress from the terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_data_availability(data, ticker_info):
    """Check if stock data is available and print message if not."""
    if data is None or data.empty:
        print(f"No data available for {ticker_info.get('longName', ticker_info.get('symbol', 'Unknown'))}")
        return True
    return False

def display_stock_summary(data, ticker_info):
    """Display a text summary of the stock data."""
    if "Volume" not in data.columns:
        return
        
    avg_volume = data["Volume"].mean()
    recent_price = data["Close"].iloc[-1]
    price_change = data["Close"].iloc[-1] - data["Close"].iloc[0]
    price_change_pct = (price_change / data["Close"].iloc[0]) * 100
    
    print(f"\nRecent Price: ${recent_price:.2f}")
    print(f"Change: ${price_change:.2f} ({price_change_pct:.2f}%)")
    print(f"Avg Volume: {int(avg_volume):,}")
    print("\nStock Information:")
    print(f"Company: {ticker_info.get('longName', ticker_info.get('symbol', 'Unknown'))}")
    print(f"Sector: {ticker_info.get('sector', 'N/A')}")
    print(f"Industry: {ticker_info.get('industry', 'N/A')}")
    
    if "marketCap" in ticker_info and ticker_info["marketCap"]:
        market_cap = ticker_info.get('marketCap', 0)
        if market_cap > 1e9:
            print(f"Market Cap: ${market_cap / 1e9:.2f}B")
        else:
            print(f"Market Cap: ${market_cap / 1e6:.2f}M")
            
    if "fiftyTwoWeekHigh" in ticker_info and "fiftyTwoWeekLow" in ticker_info:
        print(f"52-Week Range: ${ticker_info.get('fiftyTwoWeekLow', 0):.2f} - ${ticker_info.get('fiftyTwoWeekHigh', 0):.2f}")
    
    print("\n")  # Add an extra line break before the graph

def plot_price_chart(data, company_name, x_indices, date_labels, plot_type="line"):
    """Plot price data in the terminal as a chart."""
    # Clear previous plot
    plt.clf()
    
    # Set the figure size to be terminal-friendly
    plt.plotsize(70, 20)  # Adjust width and height for terminal
    
    # Plot price chart
    plt.title(f"{company_name} Stock Price")
    plt.ylabel("Price ($)")
    
    # Plot based on type
    if plot_type == "line":
        plt.plot(x_indices, data["Close"].tolist(), color="green", label="Close Price")
    elif plot_type == "candle":
        # Simulate candlestick with plotext
        for i in x_indices:
            row = data.iloc[i]
            color = "green" if row["Close"] >= row["Open"] else "red"
            plt.scatter([i], [row["High"]], color=color, marker=".")
            plt.scatter([i], [row["Low"]], color=color, marker=".")
            plt.plot([i, i], [row["Open"], row["Close"]], color=color)
    
    # Set x-ticks for price chart
    plt.xticks(x_indices, date_labels)
    
    # Show the price chart
    plt.show()

def plot_volume_chart(data, company_name, x_indices, date_labels):
    """Plot volume data in the terminal as a separate chart."""
    if "Volume" not in data.columns:
        return
        
    # Clear for volume chart
    plt.clf()
    plt.plotsize(70, 10)  # Smaller height for volume chart
    
    plt.title(f"{company_name} Volume")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.xticks(x_indices, date_labels)
    
    # Plot volume bars with colors based on price movement
    for i in x_indices:
        if i > 0:  # Skip first bar as we need previous close for comparison
            # Determine color based on price movement
            color = "green" if data["Close"].iloc[i] >= data["Close"].iloc[i-1] else "red"
            plt.bar([i], [data["Volume"].iloc[i]], color=color)
    
    # Show the volume chart
    plt.show()

def plot_stock_data(data, ticker_info, plot_type="line"):
    """Plot stock data in the terminal."""

    if check_data_availability(data, ticker_info):
        return

    # Get the company name or use the symbol if name isn't available
    company_name = ticker_info.get("longName", ticker_info.get("symbol", "Unknown"))
    
    # Display text summary of stock data
    display_stock_summary(data, ticker_info)
    
    # Prepare date labels and indices for x-axis
    dates = data.index
    date_labels = [d.strftime("%m/%d") if hasattr(d, 'strftime') else str(d)[:5] for d in dates]
    x_indices = list(range(len(dates)))
    
    # Plot the price chart
    plot_price_chart(data, company_name, x_indices, date_labels, plot_type)
    
    # Plot volume chart if data is available
    if "Volume" in data.columns:
        plot_volume_chart(data, company_name, x_indices, date_labels)
    
    # Add instruction for quick search (this will be overridden if 's' is pressed)
    print("\nPress 's' for new ticker search, 'c' to change interval, Enter to return to menu", end="", flush=True)

def prompt_for_ticker():
    """Prompt for a ticker with support for cancellation with ESC."""
    ticker = ""
    # Clear the instruction line and replace with prompt
    print("\r" + " " * 80, end="")  # Clear the current line with 80 spaces
    print("\rNew ticker: ", end="", flush=True)
    
    while True:
        char = get_key()
        
        # Handle Escape key (usually represented as '\x1b')
        if char == '\x1b':
            # Clear the current line and restore instruction
            print("\r" + " " * 80, end="")  # Clear the line completely
            print("\rPress 's' for new ticker search, 'c' to change interval, Enter to return to menu", end="", flush=True)
            return None
        
        # Handle Backspace
        elif char in ('\x7f', '\x08'):
            if ticker:
                ticker = ticker[:-1]
                # Clear the line and reprint the prompt and current ticker
                print("\r" + " " * 80, end="")
                print(f"\rNew ticker: {ticker}", end="", flush=True)
        
        # Handle Enter key
        elif char in ('\r', '\n'):
            print()  # Move to the next line
            return ticker.strip().upper()
        
        # Handle other printable characters
        elif char.isprintable():
            ticker += char
            print(char, end="", flush=True)

def prompt_for_interval(current_period):
    """Prompt user to select a candlestick interval."""
    clear_screen()
    print("\n==== Select Candlestick Interval ====")
    
    # Define available intervals based on the period
    # Note: YFinance has limitations on which intervals can be used with certain periods
    if current_period in ["1d", "5d"]:
        print("1. 1 minute")
        print("2. 2 minutes")
        print("3. 5 minutes")
        print("4. 15 minutes")
        print("5. 30 minutes")
        print("6. 1 hour (default)")
        print("7. 1 day")
        
        interval_map = {
            "1": "1m",
            "2": "2m",
            "3": "5m",
            "4": "15m",
            "5": "30m",
            "6": "1h",
            "7": "1d"
        }
    elif current_period in ["1mo", "3mo"]:
        print("1. 30 minutes")
        print("2. 1 hour")
        print("3. 1 day (default)")
        print("4. 5 days")
        print("5. 1 week")
        
        interval_map = {
            "1": "30m",
            "2": "1h",
            "3": "1d",
            "4": "5d",
            "5": "1wk"
        }
    else:  # Longer periods
        print("1. 1 day (default)")
        print("2. 5 days")
        print("3. 1 week")
        print("4. 1 month")
        
        interval_map = {
            "1": "1d",
            "2": "5d",
            "3": "1wk",
            "4": "1mo"
        }
    
    print("\nPress ESC to cancel")
    
    # Get choice
    choice = ""
    while True:
        char = get_key()
        
        # Handle Escape key
        if char == '\x1b':
            return None
        
        # Handle Backspace
        elif char in ('\x7f', '\x08'):
            if choice:
                choice = choice[:-1]
                print("\rChoice: " + choice + " \b", end="", flush=True)
        
        # Handle Enter key
        elif char in ('\r', '\n'):
            print()  # Move to the next line
            if not choice:  # Default
                if current_period in ["1d", "5d"]:
                    return "1h"
                else:
                    return "1d"
            return interval_map.get(choice, "1d") 