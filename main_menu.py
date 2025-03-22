import term_chart as tc
from stock_data import get_stock_data

def main_menu():
    """Display main menu and get user input."""
    # Default settings
    current_period = "6mo"
    current_chart_type = "line"
    current_interval = "1d"  # Default interval
    
    while True:
        tc.clear_screen()
        print("\n==== Terminal Stock Chart Application ====")
        print("\nEnter a ticker symbol (e.g., AAPL, MSFT, GOOGL)")
        print("Type 'exit' to quit")
        
        ticker = input("\nTicker: ").strip().upper()
        
        if ticker.lower() == 'exit':
            print("Goodbye!")
            break
        
        if not ticker:
            continue
        
        # Only show period selection if we don't have a saved one
        if not current_period:
            # Time period options
            tc.clear_screen()
            print(f"\nSelected ticker: {ticker}")
            print("\nSelect time period:")
            print("1. 1 Day")
            print("2. 5 Days")
            print("3. 1 Month")
            print("4. 3 Months")
            print("5. 6 Months (default)")
            print("6. 1 Year")
            print("7. 5 Years")
            
            period_choice = input("\nChoice (1-7), press Enter for default: ")
            
            period_map = {
                "1": "1d", 
                "2": "5d", 
                "3": "1mo", 
                "4": "3mo", 
                "5": "6mo", 
                "6": "1y", 
                "7": "5y"
            }
            
            # Default to 6 months (option 5)
            if period_choice == "":
                current_period = "6mo"
            else:
                current_period = period_map.get(period_choice, "6mo")
        
        # Only show chart type selection if we don't have a saved one
        if not current_chart_type:
            # Chart type options
            tc.clear_screen()
            print(f"\nSelected ticker: {ticker} for period: {current_period}")
            print("\nSelect chart type:")
            print("1. Line Chart (default)")
            print("2. Candlestick Chart")
            
            chart_choice = input("\nChoice (1-2), press Enter for default: ")
            # Default to line chart
            if chart_choice == "" or chart_choice == "1":
                current_chart_type = "line"
            elif chart_choice == "2":
                current_chart_type = "candle"
            else:
                current_chart_type = "line"  # Fallback to line chart for invalid inputs
        
        # Process for continuous lookups
        while True:
            # Fetch and display data
            tc.clear_screen()
            print(f"\nFetching data for {ticker}...")
            print(f"Using period: {current_period}, chart type: {current_chart_type}, interval: {current_interval}")
            
            try:
                data, info = get_stock_data(ticker, period=current_period, interval=current_interval)
                if data is not None and not data.empty:
                    try:
                        print(f"Plotting {current_chart_type} chart for {ticker}...")
                        tc.plot_stock_data(data, info, plot_type=current_chart_type, interval=current_interval, timeframe=current_period)
                    except Exception as e:
                        print(f"Error plotting data: {str(e)}")
                        print("Basic stock information:")
                        for key in ['longName', 'symbol', 'sector', 'industry']:
                            if key in info:
                                print(f"{key}: {info[key]}")
                else:
                    print(f"Error fetching data for {ticker}. Please check the ticker symbol and try again.")
                    input("\nPress Enter to continue...")
                    break
            except Exception as e:
                print(f"Error in data processing: {str(e)}")
                input("\nPress Enter to continue...")
                break
            
            # Get key press
            key = tc.get_key()
            
            # 's' key for new search
            if key.lower() == 's':
                new_ticker = tc.prompt_for_ticker()
                if new_ticker:
                    ticker = new_ticker
                    continue  # Stay in the inner loop with the new ticker
                else:
                    # User canceled the search, continue showing current ticker
                    continue
            # 'c' key for changing interval
            elif key.lower() == 'c':
                new_interval = tc.prompt_for_interval(current_period)
                if new_interval:
                    current_interval = new_interval
                continue  # Stay in the inner loop with the new interval
            # 't' key for changing time frame
            elif key.lower() == 't':
                new_timeframe = tc.prompt_for_timeframe()
                if new_timeframe:
                    # Check if new_timeframe is a tuple (timeframe, interval)
                    if isinstance(new_timeframe, tuple):
                        current_period, current_interval = new_timeframe
                    else:
                        current_period = new_timeframe
                continue  # Stay in the inner loop with the new time frame
            else:
                # Any other key returns to main menu
                break 