#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "yfinance>=0.2.0",
# ]
# ///
"""
Fetch current stock price using yfinance library.

Usage:
    uv run get_stock_price.py MSFT
    uv run get_stock_price.py AAPL --json
"""
import argparse
import sys
from decimal import Decimal

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance library is not installed.", file=sys.stderr)
    print("Install it with: uv add yfinance", file=sys.stderr)
    sys.exit(2)


def get_current_price(symbol: str) -> dict:
    """
    Get the current stock price for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'MSFT', 'AAPL', 'GOOGL')
    
    Returns:
        Dictionary with price information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price - try different fields based on what's available
        current_price = (
            info.get('currentPrice') or 
            info.get('regularMarketPrice') or 
            info.get('previousClose')
        )
        
        if current_price is None:
            return {
                'success': False,
                'error': f"Could not fetch price for {symbol}. Symbol may not exist or market data unavailable."
            }
        
        # Get additional useful information
        company_name = info.get('longName') or info.get('shortName') or symbol
        currency = info.get('currency', 'USD')
        
        return {
            'success': True,
            'symbol': symbol.upper(),
            'company_name': company_name,
            'current_price': current_price,
            'currency': currency,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Error fetching data for {symbol}: {str(e)}"
        }


def format_price(price_info: dict) -> str:
    """Format price information as human-readable string."""
    if not price_info['success']:
        return price_info['error']
    
    symbol = price_info['symbol']
    company = price_info['company_name']
    price = price_info['current_price']
    currency = price_info['currency']
    
    return f"{company} ({symbol}): {currency} {price:.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current stock price using yfinance"
    )
    parser.add_argument(
        'symbol',
        help='Stock ticker symbol (e.g., MSFT, AAPL, GOOGL)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of formatted text'
    )
    
    args = parser.parse_args()
    
    price_info = get_current_price(args.symbol)
    
    if args.json:
        import json
        print(json.dumps(price_info, indent=2))
    else:
        print(format_price(price_info))
    
    return 0 if price_info['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
