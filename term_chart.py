import os
import sys
import termios
import tty
import plotext as plt
import pandas as pd

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

def plot_price_chart(data, company_name, x_indices, date_labels, plot_type="line", interval="1d", timeframe="1mo"):
    """Plot price data in the terminal as a chart."""
    # Clear previous plot
    plt.clf()
    
    # Get terminal size and set the figure size to match terminal width
    terminal_width, _ = os.get_terminal_size()
    plt.plotsize(terminal_width - 5, 20)  # Subtract a small margin for safety
    
    # Plot price chart with interval and timeframe in the title
    plt.title(f"{company_name} ({interval} : {timeframe})")
    plt.ylabel("Price ($)")
    
    # Plot based on type
    if plot_type == "line":
        plt.plot(x_indices, data["Close"].tolist(), color="green", label=f"{interval} : {timeframe}")
    elif plot_type == "candle":
        # Simulate candlestick with plotext
        for i in x_indices:
            row = data.iloc[i]
            color = "green" if row["Close"] >= row["Open"] else "red"
            plt.scatter([i], [row["High"]], color=color, marker=".")
            plt.scatter([i], [row["Low"]], color=color, marker=".")
            plt.plot([i, i], [row["Open"], row["Close"]], color=color)
    
    # Add adaptive SMA to the main chart if enough data is available
    if len(data) >= 10:  # Require at least 10 data points
        # Calculate adaptive SMA period
        sma_period = max(10, min(200, len(data) // 4))
        sma_column = f'SMA_{sma_period}'
        
        # Calculate SMA if not already calculated
        if sma_column not in data.columns:
            data[sma_column] = data['Close'].rolling(window=sma_period).mean()
        
        # Filter out NaN values from SMA
        valid_indices = [i for i in x_indices if i >= (sma_period-1) and not pd.isna(data[sma_column].iloc[i])]
        valid_sma = [data[sma_column].iloc[i] for i in valid_indices]
        
        if valid_indices:
            plt.plot(valid_indices, valid_sma, color="blue", label=f"{sma_period}-SMA")
    
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
    
    # Get terminal size and set the figure size to match terminal width
    terminal_width, _ = os.get_terminal_size()
    plt.plotsize(terminal_width - 5, 10)  # Subtract a small margin for sgafety
    
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

def plot_sma_chart(data, company_name, x_indices, date_labels):
    """Plot SMA in the terminal as a separate chart, adapting to available data."""
    if "Close" not in data.columns or len(data) < 10:  # Require at least 10 data points
        print("Not enough data for SMA (need at least 10 data points)")
        return
        
    # Calculate adaptive SMA period based on available data
    # Use 1/4 of available data points, with a minimum of 10 and maximum of 200
    sma_period = max(10, min(200, len(data) // 4))
    
    # Calculate SMA with adaptive period
    sma_column = f'SMA_{sma_period}'
    if sma_column not in data.columns:
        data[sma_column] = data['Close'].rolling(window=sma_period).mean()
    
    # Clear for SMA chart
    plt.clf()
    
    # Get terminal size and set the figure size to match terminal width
    terminal_width, _ = os.get_terminal_size()
    plt.plotsize(terminal_width - 5, 10)  # Subtract a small margin for safety
    
    plt.title(f"{company_name} {sma_period}-SMA")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.xticks(x_indices, date_labels)
    
    # Create a full list of x-indices to maintain alignment with main chart
    # Fill with None for points where SMA is not available
    full_sma_values = [None] * len(x_indices)
    
    # Fill in the SMA values where they exist
    for i in x_indices:
        if i >= (sma_period-1) and not pd.isna(data[sma_column].iloc[i]):
            full_sma_values[i] = data[sma_column].iloc[i]
    
    # Filter out None values for plotting
    valid_indices = [i for i in x_indices if full_sma_values[i] is not None]
    valid_sma = [full_sma_values[i] for i in valid_indices]
    
    if valid_indices:
        # Plot the SMA line
        plt.plot(valid_indices, valid_sma, color="blue", label=f"{sma_period}-SMA")
        
        # Set the x-axis limits to match the main chart
        plt.xlim(min(x_indices), max(x_indices))
    else:
        print("No valid SMA data points to plot")
    
    # Show the SMA chart
    plt.show()

def plot_stock_data(data, ticker_info, plot_type="line", interval="1d", timeframe="1mo"):
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
    
    # Plot the price chart with interval and timeframe
    plot_price_chart(data, company_name, x_indices, date_labels, plot_type, interval, timeframe)
    
    # Plot volume chart if data is available
    if "Volume" in data.columns:
        plot_volume_chart(data, company_name, x_indices, date_labels)
    
    # Add instruction for quick search (this will be overridden if 's' is pressed)
    print("\nPress 's' for new ticker search, 'c' to change interval, 't' to change time frame, Enter to return to menu", end="", flush=True)

def prompt_for_ticker():
    """Prompt for a ticker with support for cancellation with ESC."""
    ticker = ""
    # Store the original instruction for restoration
    original_instruction = "Press 's' for new ticker search, 'c' to change interval, 't' to change time frame, Enter to return to menu"
    
    # Get terminal width to ensure we clear the entire line
    try:
        terminal_width, _ = os.get_terminal_size()
    except:
        terminal_width = 120  # Fallback if we can't get terminal size
    
    # Clear the instruction line and replace with prompt
    print("\r" + " " * terminal_width, end="")  # Clear the current line with spaces
    print("\rNew ticker: ", end="", flush=True)
    
    while True:
        char = get_key()
        
        # Handle Escape key (usually represented as '\x1b')
        if char == '\x1b':
            # Clear the current line and restore instruction
            print("\r" + " " * terminal_width, end="")  # Clear the line completely
            print(f"\r{original_instruction}", end="", flush=True)
            return None
        
        # Handle Backspace
        elif char in ('\x7f', '\x08'):
            if ticker:
                ticker = ticker[:-1]
                # Clear the line and reprint the prompt and current ticker
                print("\r" + " " * terminal_width, end="")
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
        print("3. 5 minutes (default for 1d)")
        print("4. 15 minutes")
        print("5. 30 minutes")
        print("6. 60 minutes")
        print("7. 90 minutes")
        print("8. 1 hour")  # Added explicitly for clarity
        print("9. 1 day")
        
        interval_map = {
            "1": "1m",
            "2": "2m",
            "3": "5m",
            "4": "15m",
            "5": "30m",
            "6": "60m",
            "7": "90m",
            "8": "1h",  # Added explicitly for clarity
            "9": "1d"
        }
    elif current_period in ["1mo", "3mo"]:
        print("1. 30 minutes")
        print("2. 60 minutes")
        print("3. 90 minutes")
        print("4. 1 hour")  # Added explicitly for clarity
        print("5. 1 day (default)")
        print("6. 5 days")
        print("7. 1 week")
        
        interval_map = {
            "1": "30m",
            "2": "60m",
            "3": "90m",
            "4": "1h",  # Added explicitly for clarity
            "5": "1d",
            "6": "5d",
            "7": "1wk"
        }
    else:  # Longer periods
        print("1. 1 hour")
        print("2. 1 day (default)")
        print("3. 5 days")
        print("4. 1 week")
        print("5. 1 month")
        print("6. 3 months")
        
        interval_map = {
            "1": "1h",
            "2": "1d",
            "3": "5d",
            "4": "1wk",
            "5": "1mo",
            "6": "3mo"
        }
    
    print("\nPress ESC to cancel")
    
    # Wait for a single keypress
    while True:
        char = get_key()
        
        # Handle Escape key
        if char == '\x1b':
            return None
        
        # Handle digit keys (immediate selection)
        elif char.isdigit() and char in interval_map:
            print(f"\nSelected: {char}")
            return interval_map[char]
        
        # Default if any other key is pressed
        elif char in ('\r', '\n'):
            # Return default value based on period
            if current_period == "1d":
                return "5m"  # Default to 5-minute chart for 1-day period
            elif current_period == "5d":
                return "1h"  # Keep 1-hour default for 5-day period
            else:
                return "1d"  # Default to 1-day for longer periods

def prompt_for_timeframe():
    """Prompt user to select a time frame (period)."""
    clear_screen()
    print("\n==== Select Time Frame ====")
    print("1. 1 Day")
    print("2. 10 Days")
    print("3. 1 Month")
    print("4. 3 Months")
    print("5. 6 Months")
    print("6. Year to Date (YTD)")
    print("7. 1 Year")
    print("8. 2 Years")
    print("9. 5 Years")
    print("0. Max")  # Changed to 0 for single-key selection
    
    print("\nPress ESC to cancel")
    
    timeframe_map = {
        "1": "1d",
        "2": "10d",
        "3": "1mo",
        "4": "3mo",
        "5": "6mo",
        "6": "ytd",
        "7": "1y",
        "8": "2y",
        "9": "5y",
        "0": "max"  # Changed to 0 for single-key selection
    }
    
    # Get the current interval to check if it's a minute chart
    # This will need to be passed in from the calling function
    current_interval = getattr(prompt_for_timeframe, 'current_interval', None)
    is_minute_chart = current_interval in ["1m", "2m", "5m", "15m", "30m"] if current_interval else False
    
    # Wait for a single keypress
    while True:
        char = get_key()
        
        # Handle Escape key
        if char == '\x1b':
            return None
        
        # Handle digit keys (immediate selection)
        elif char.isdigit() and char in timeframe_map:
            print(f"\nSelected: {char}")
            selected_timeframe = timeframe_map[char]
            
            # Set default intervals for specific timeframes
            if selected_timeframe == "1d":
                return (selected_timeframe, "1m")
            elif selected_timeframe == "10d":
                return (selected_timeframe, "1h")
            # For other timeframes, if coming from a minute chart, set to hourly
            elif is_minute_chart:
                return (selected_timeframe, "1h")
            
            # For other timeframes, just return the timeframe
            return selected_timeframe
        
        # Default if any other key is pressed
        elif char in ('\r', '\n'):
            return "1mo"  # Default to 1 month 