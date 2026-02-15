---
name: yfinance
description: Fetch current stock prices using Yahoo Finance API. Use when you need to get real-time stock market data, check current stock prices, or retrieve stock ticker information.
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "python-brew",
              "kind": "brew",
              "formula": "python",
              "bins": ["python3"],
              "label": "Install Python (brew)",
            },
            {
              "id": "python-apt",
              "kind": "apt",
              "package": "python3",
              "bins": ["python3"],
              "label": "Install Python (apt)",
            },
          ],
      },
  }
---

# Yahoo Finance Stock Price

Get current stock prices using the `yfinance` Python library. No API key required.

## Installation

The script requires the `yfinance` library:

```bash
pip install yfinance
```

## Usage

Get current stock price for a symbol:

```bash
python3 {baseDir}/scripts/get_stock_price.py MSFT
# Output: Microsoft Corporation (MSFT): USD 374.51
```

Get price for other stocks:

```bash
python3 {baseDir}/scripts/get_stock_price.py AAPL
python3 {baseDir}/scripts/get_stock_price.py GOOGL
python3 {baseDir}/scripts/get_stock_price.py TSLA
```

## JSON Output

For programmatic use, add the `--json` flag:

```bash
python3 {baseDir}/scripts/get_stock_price.py MSFT --json
```

Example output:

```json
{
  "success": true,
  "symbol": "MSFT",
  "company_name": "Microsoft Corporation",
  "current_price": 374.51,
  "currency": "USD"
}
```

## Error Handling

If the stock symbol is invalid or data is unavailable, the script will indicate failure:

```bash
python3 {baseDir}/scripts/get_stock_price.py INVALID
# Output: Could not fetch price for INVALID. Symbol may not exist or market data unavailable.
```

With JSON output:

```json
{
  "success": false,
  "error": "Could not fetch price for INVALID. Symbol may not exist or market data unavailable."
}
```

## Supported Symbols

The script works with:
- US stocks (NYSE, NASDAQ): `MSFT`, `AAPL`, `GOOGL`, etc.
- International stocks: `TSLA`, `NVDA`, etc.
- ETFs: `SPY`, `QQQ`, etc.
- Indices: `^GSPC` (S&P 500), `^DJI` (Dow Jones), `^IXIC` (NASDAQ)

## Notes

- Prices are fetched in real-time from Yahoo Finance
- The script returns the most current available price (currentPrice, regularMarketPrice, or previousClose)
- Internet connection required for the script to function
- Data quality and availability depends on Yahoo Finance's service
