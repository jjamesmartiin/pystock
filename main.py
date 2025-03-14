import yfinance as yf
import pandas as pd
import numpy as np
import plotext as plt
import datetime
import time
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_stock_data(ticker, period="1mo", interval="1d"):
    """Fetch stock data using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data, stock.info
    except Exception as e:
        return None, {"longName": ticker, "error": str(e)}

def plot_stock_data(data, ticker_info, plot_type="line"):
    """Plot stock data in the terminal."""
    if data is None or data.empty:
        print(f"No data available for {ticker_info.get('longName', ticker_info.get('symbol', 'Unknown'))}")
        return


    # Get the company name or use the symbol if name isn't available
    company_name = ticker_info.get("longName", ticker_info.get("symbol", "Unknown"))
    
    # Instead of using dates as strings, use numerical indices for x-axis
    # and format dates as labels
    dates = data.index
    date_labels = [d.strftime("%m/%d") if hasattr(d, 'strftime') else str(d)[:5] for d in dates]
    x_indices = list(range(len(dates)))
    
    # Clear previous plot
    plt.clf()
    
    # Set plot title and labels
    plt.title(f"{company_name} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    
    # Use numerical x values with date labels
    plt.xticks(x_indices, date_labels)
    
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
    
    # Show the plot
    plt.show()
    
    # Instead of figtext, print additional information below the plot
    if "Volume" in data.columns:
        avg_volume = data["Volume"].mean()
        recent_price = data["Close"].iloc[-1]
        price_change = data["Close"].iloc[-1] - data["Close"].iloc[0]
        price_change_pct = (price_change / data["Close"].iloc[0]) * 100
        
        print(f"\nRecent Price: ${recent_price:.2f}")
        print(f"Change: ${price_change:.2f} ({price_change_pct:.2f}%)")
        print(f"Avg Volume: {int(avg_volume):,}")

def main_menu():
    """Display main menu and get user input."""
    while True:
        clear_screen()
        print("\n==== Terminal Stock Chart Application ====")
        print("\nEnter a ticker symbol (e.g., AAPL, MSFT, GOOGL)")
        print("Type 'exit' to quit")
        
        ticker = input("\nTicker: ").strip().upper()
        
        if ticker.lower() == 'exit':
            print("Goodbye!")
            break
        
        if not ticker:
            continue
        
        # Time period options
        clear_screen()
        print(f"\nSelected ticker: {ticker}")
        print("\nSelect time period:")
        print("1. 1 Day")
        print("2. 5 Days")
        print("3. 1 Month")
        print("4. 3 Months")
        print("5. 6 Months")
        print("6. 1 Year")
        print("7. 5 Years")
        
        period_choice = input("\nChoice (1-7): ")
        
        period_map = {
            "1": "1d", 
            "2": "5d", 
            "3": "1mo", 
            "4": "3mo", 
            "5": "6mo", 
            "6": "1y", 
            "7": "5y"
        }
        
        period = period_map.get(period_choice, "1mo")
        
        # Chart type options

        clear_screen()
        print(f"\nSelected ticker: {ticker} for period: {period}")
        print("\nSelect chart type:")
        print("1. Line Chart")
        print("2. Candlestick Chart")
        
        chart_choice = input("\nChoice (1-2): ")
        chart_type = "candle" if chart_choice == "2" else "line"
        
        # Fetch and display data
        clear_screen()
        print(f"\nFetching data for {ticker}...")
        data, info = get_stock_data(ticker, period=period)
        
        if data is not None and not data.empty:
            try:
                plot_stock_data(data, info, plot_type=chart_type)
                
                # Display some additional info
                print("\nStock Information:")
                print(f"Company: {info.get('longName', ticker)}")
                print(f"Sector: {info.get('sector', 'N/A')}")
                print(f"Industry: {info.get('industry', 'N/A')}")
                
                if "marketCap" in info and info["marketCap"]:
                    market_cap = info.get('marketCap', 0)
                    if market_cap > 1e9:
                        print(f"Market Cap: ${market_cap / 1e9:.2f}B")
                    else:
                        print(f"Market Cap: ${market_cap / 1e6:.2f}M")
                        
                if "fiftyTwoWeekHigh" in info and "fiftyTwoWeekLow" in info:
                    print(f"52-Week Range: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}")
            except Exception as e:
                print(f"Error plotting data: {str(e)}")
                print("Basic stock information:")
                for key in ['longName', 'symbol', 'sector', 'industry']:
                    if key in info:
                        print(f"{key}: {info[key]}")
        else:
            print(f"Error fetching data for {ticker}. Please check the ticker symbol and try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
