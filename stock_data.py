import yfinance as yf

def get_stock_data(ticker, period="1mo", interval="1d"):
    """Fetch stock data using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data, stock.info
    except Exception as e:
        return None, {"longName": ticker, "error": str(e)} 