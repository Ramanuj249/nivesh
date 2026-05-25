"""
tools/stock_tools.py
──────────────────────────────────────────────────
Live NSE/BSE stock data using yfinance.
All agents use these tools to fetch real market data.

Industry standards used:
- Logger for every action — no print() statements
- Cache for every API call — avoid redundant yfinance hits
- Error handling on every function — never crash the agent
- Type hints on every function — clear contracts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from langchain_core.tools import tool
from settings import logger, cache_get, cache_set

def get_ticker(symbol: str)-> str:
    """convert Indian stock to yfinance formate."""
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    return f"{symbol}.NS"

# -----tool 1: Live Price----------------------------------
@tool()
def get_stock_price(symbol: str) -> str:
    """Get the current live price and basic info for an Indian stock."""

    logger.info(f"Fetching live price for: {symbol}")

    cache_key = f"{symbol}_price"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Returning cached price for {symbol}")
        return cached

    try:
        ticker = get_ticker(symbol)
        stock = yf.Ticker(ticker)
        info = stock.info

        price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        prev_close = info.get("previousClose", "N/A")

        if price != "N/A" and prev_close != "N/A":
            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2)
        else:
            change = "N/A"
            change_pct = "N/A"
        result = f"""
        Stock        : {info.get('longName', symbol)}
        Symbol       : {ticker}
        Price        : ₹{price}
        Change       : ₹{change} ({change_pct}%)
        Day High     : ₹{info.get('dayHigh', 'N/A')}
        Day Low      : ₹{info.get('dayLow', 'N/A')}
        52W High     : ₹{info.get('fiftyTwoWeekHigh', 'N/A')}
        52W Low      : ₹{info.get('fiftyTwoWeekLow', 'N/A')}
        Volume       : {info.get('volume', 'N/A'):,}
        Market Cap   : ₹{info.get('marketCap', 'N/A'):,}
        """
        cache_set(cache_key, result)
        logger.info(f"Price fetched successfully for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        return f"Error fetching price for {symbol}: {e}"

# ----- tool 2: Fundamental Analysis
@tool()
def get_fundamental_data(symbol: str)-> str:
    """Get fundamental financial data for an Indian stock."""
    logger.info(f"Fetching fundamental data for: {symbol}")

    cache_key = f"{symbol}_fundamental"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Returning cached fundamental data for {symbol}")
        return cached

    try:
        ticker = get_ticker(symbol)
        stock = yf.Ticker(ticker)
        info = stock.info

        result = f"""
        Company      : {info.get('longName', symbol)}
        Sector       : {info.get('sector', 'N/A')}
        Industry     : {info.get('industry', 'N/A')}
         
        --- Valuation ---
        P/E Ratio    : {info.get('trailingPE', 'N/A')}
        P/B Ratio    : {info.get('priceToBook', 'N/A')}
        EV/EBITDA    : {info.get('enterpriseToEbitda', 'N/A')}
         
        --- Profitability ---
        EPS          : ₹{info.get('trailingEps', 'N/A')}
        ROE          : {round(info.get('returnOnEquity', 0) * 100, 2)}%
        ROA          : {round(info.get('returnOnAssets', 0) * 100, 2)}%
        Profit Margin: {round(info.get('profitMargins', 0) * 100, 2)}%
         
        --- Growth ---
        Revenue      : ₹{info.get('totalRevenue', 'N/A'):,}
        Revenue Growth: {round(info.get('revenueGrowth', 0) * 100, 2)}%
        Earnings Growth: {round(info.get('earningsGrowth', 0) * 100, 2)}%
         
        --- Financial Health ---
        Total Debt   : ₹{info.get('totalDebt', 'N/A'):,}
        Debt/Equity  : {info.get('debtToEquity', 'N/A')}
        Current Ratio: {info.get('currentRatio', 'N/A')}
        Free Cash Flow: ₹{info.get('freeCashflow', 'N/A'):,}
         
        --- Dividends ---
        Dividend Yield: {round(info.get('dividendYield', 0) * 100, 2)}%
        """
        cache_set(cache_key, result)
        logger.info(f"Fundamental data fetched successfully for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch fundamental data for {symbol}: {e}")
        return f"Error fetching fundamental data for {symbol}: {e}"

# ----- TOOL 3 — Price History + Technical Indicators ---------
@tool
def get_price_history(symbol: str, period: str = "6mo") -> str:
    """Get historical price data with technical indicators."""

    logger.info(f"Fetching price history for: {symbol} | period: {period}")

    cache_key = f"{symbol}_history_{period}"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Returning cached history for {symbol}")
        return cached

    try:
        ticker = get_ticker(symbol)
        stock  = yf.Ticker(ticker)
        hist   = stock.history(period=period)

        if hist.empty:
            logger.warning(f"No historical data found for {symbol}")
            return f"No historical data found for {symbol}"

        hist["MA50"]  = hist["Close"].rolling(window=50).mean()
        hist["MA200"] = hist["Close"].rolling(window=200).mean()

        delta  = hist["Close"].diff()
        gain   = delta.where(delta > 0, 0).rolling(14).mean()
        loss   = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs     = gain / loss
        hist["RSI"] = 100 - (100 / (1 + rs))

        latest  = hist.iloc[-1]
        first   = hist.iloc[0]
        returns = round(((latest["Close"] - first["Close"]) / first["Close"]) * 100, 2)

        ma50  = latest["MA50"]
        ma200 = latest["MA200"]
        price = latest["Close"]
        rsi   = latest["RSI"]

        if pd.notna(ma50) and pd.notna(ma200):
            if price > ma50 > ma200:
                trend = "BULLISH — price above both MA50 and MA200"
            elif price < ma50 < ma200:
                trend = "BEARISH — price below both MA50 and MA200"
            else:
                trend = "NEUTRAL — mixed signals"
        else:
            trend = "Insufficient data for trend"

        rsi_signal = ("OVERBOUGHT" if pd.notna(rsi) and rsi > 70
                      else "OVERSOLD" if pd.notna(rsi) and rsi < 30
                      else "NEUTRAL")

        result = f"""
        Period         : {period}
        Start Price    : ₹{round(first['Close'], 2)}
        Current Price  : ₹{round(latest['Close'], 2)}
        Period Return  : {returns}%
         
        --- Technical Indicators ---
        50 Day MA      : ₹{round(ma50, 2) if pd.notna(ma50) else 'N/A'}
        200 Day MA     : ₹{round(ma200, 2) if pd.notna(ma200) else 'N/A'}
        RSI (14)       : {round(rsi, 2) if pd.notna(rsi) else 'N/A'}
         
        --- Signals ---
        Trend          : {trend}
        RSI Signal     : {rsi_signal}
         
        --- Price Range ---
        Period High    : ₹{round(hist['High'].max(), 2)}
        Period Low     : ₹{round(hist['Low'].min(), 2)}
        Avg Volume     : {int(hist['Volume'].mean()):,}
        """
        cache_set(cache_key, result)
        logger.info(f"History fetched successfully for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch history for {symbol}: {e}")
        return f"Error fetching history for {symbol}: {e}"

# ----- TOOL 4 — Peer Comparison -------------------------
@tool
def get_peer_comparison(symbol: str) -> str:
    """Compare stock against top peers in the same sector."""

    logger.info(f"Fetching peer comparison for: {symbol}")

    cache_key = f"{symbol}_peers"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Returning cached peer data for {symbol}")
        return cached

    try:
        ticker = get_ticker(symbol)
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get("sector", "N/A")

        peers_map = {
            "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
            "Financial Services": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"],
            "Energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS"],
            "Automobile": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS"],
            "Consumer Defensive": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "DABUR.NS"],
            "Healthcare": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
        }

        peers = [p for p in peers_map.get(sector, [])
                 if not p.startswith(symbol.upper())][:3]

        if not peers:
            return f"Sector: {sector}\nNo peer data available."

        result = f"Sector: {sector}\n\n--- Peer Comparison ---\n"
        result += f"{'Company':<22} {'Price':>10} {'P/E':>8} {'Market Cap':>15}\n"
        result += "─" * 57 + "\n"

        for peer in peers:
            try:
                p_info = yf.Ticker(peer).info
                name = p_info.get("shortName", peer)[:20]
                price = p_info.get("currentPrice", "N/A")
                pe = round(p_info.get("trailingPE", 0), 1)
                mcap = p_info.get("marketCap", 0)
                mcap_cr = f"₹{round(mcap / 10000000):,}Cr" if mcap else "N/A"
                result += f"{name:<22} {str(price):>10} {str(pe):>8} {mcap_cr:>15}\n"
            except Exception as pe_err:
                logger.warning(f"Could not fetch peer data for {peer}: {pe_err}")
                continue

        cache_set(cache_key, result)
        logger.info(f"Peer comparison done for {symbol}")
        return result

    except Exception as e:
        logger.error(f"Failed peer comparison for {symbol}: {e}")
        return f"Error fetching peer data for {symbol}: {e}"


# Quick test
if __name__ == "__main__":
    logger.info("Running stock_tools test...")
    print(get_stock_price.invoke({"symbol": "PREMIERENE"}))
    print(get_fundamental_data.invoke({"symbol": "PREMIERENE"}))
    print(get_price_history.invoke({"symbol": "PREMIERENE", "period": "3mo"}))
    print(get_peer_comparison.invoke({"symbol": "PREMIERENE"}))
