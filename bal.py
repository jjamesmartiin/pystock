import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def get_balance_sheet(ticker_symbol):
    """
    Fetches and returns balance sheet data for the given ticker symbol.
    """
    print(f"Fetching balance sheet data for {ticker_symbol}...")
    
    # Create a Ticker object
    ticker = yf.Ticker(ticker_symbol)
    
    # Get the balance sheet data
    balance_sheet = ticker.balance_sheet
    
    return balance_sheet

def format_balance_sheet(balance_sheet):
    """
    Formats the balance sheet data for better readability.
    Converts values to millions and rounds to 2 decimal places.
    """
    # Convert to millions for better readability
    formatted_bs = balance_sheet / 1_000_000
    
    # Round to 2 decimal places
    formatted_bs = formatted_bs.round(2)
    
    return formatted_bs

def display_balance_sheet(balance_sheet, ticker_symbol):
    """
    Displays the balance sheet in a formatted way.
    """
    print(f"\nBalance Sheet for {ticker_symbol} (in millions):")
    print("=" * 80)
    
    # Display the formatted balance sheet
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.width', 1000)     # Wider display
    print(balance_sheet)
    
    # Reset display options
    pd.reset_option('display.max_rows')
    pd.reset_option('display.width')

def display_key_metrics(balance_sheet, ticker_symbol):
    """
    Extracts and displays key balance sheet metrics.
    """
    print(f"\nKey Balance Sheet Metrics for {ticker_symbol} (in millions):")
    print("=" * 80)
    
    try:
        # Find Total Assets
        total_assets = balance_sheet.loc['Total Assets']
        print(f"Total Assets:")
        for date, value in total_assets.items():
            print(f"  {date.strftime('%Y-%m-%d')}: {value:.2f}")
        
        # Find Total Liabilities
        try:
            liability_row = 'Total Liabilities Net Minority Interest'
            total_liabilities = balance_sheet.loc[liability_row]
        except KeyError:
            try:
                liability_row = 'Total Liabilities'
                total_liabilities = balance_sheet.loc[liability_row]
            except KeyError:
                print("\nCouldn't find standard liability rows. Available row labels are:")
                print("\n".join(balance_sheet.index.tolist()))
                return
                
        print(f"\n{liability_row}:")
        for date, value in total_liabilities.items():
            print(f"  {date.strftime('%Y-%m-%d')}: {value:.2f}")
        
        # Calculate and display shareholders' equity
        shareholders_equity = total_assets - total_liabilities
        print(f"\nShareholders' Equity (Assets - Liabilities):")
        for date, value in shareholders_equity.items():
            print(f"  {date.strftime('%Y-%m-%d')}: {value:.2f}")
            
    except Exception as e:
        print(f"Error extracting key metrics: {e}")

def save_to_csv(balance_sheet, ticker_symbol):
    """
    Saves the balance sheet to a CSV file.
    """
    output_dir = 'financial_data'
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/{ticker_symbol}_balance_sheet_{timestamp}.csv"
    
    # Save to CSV
    balance_sheet.to_csv(filename)
    print(f"\nBalance sheet saved to '{filename}'")
    
    return filename

def main():
    # Get ticker symbol from user
    ticker_symbol = input("Enter the ticker symbol (e.g., AAPL for Apple Inc.): ").strip().upper()
    
    try:
        # Get balance sheet data
        balance_sheet = get_balance_sheet(ticker_symbol)
        
        if balance_sheet.empty:
            print(f"No balance sheet data available for {ticker_symbol}.")
            return
            
        # Format the balance sheet
        formatted_bs = format_balance_sheet(balance_sheet)
        
        # Display the formatted balance sheet
        display_balance_sheet(formatted_bs, ticker_symbol)
        
        # Display key metrics
        display_key_metrics(formatted_bs, ticker_symbol)
        
        # Ask user if they want to save to CSV
        save_option = input("\nWould you like to save the balance sheet to a CSV file? (y/n): ").strip().lower()
        if save_option == 'y':
            save_to_csv(formatted_bs, ticker_symbol)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please check if the ticker symbol is valid and try again.")

if __name__ == "__main__":
    main()
