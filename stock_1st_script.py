
import yfinance as yf
import pandas as pd

# Pick any stock ticker you want to study

ticker = "KO" # Micron Technology
stock = yf.Ticker(ticker)


# Pull key facts
info = stock.info
print("Company :", info.get("longName"))
print("Price :", info.get("currentPrice"))
print("P/E :", info.get("trailingPE"))
print("Yield :", info.get("dividendYield"))
print("Sector :", info.get("sector"))


# Pull 3 months of price history
history = stock.history(period="3mo")
print(history.tail(5)) # show last 5 days

# Save to Excel — open it like any spreadsheet
history.index = history.index.tz_localize(None)
history.to_excel("/Users/beckylin/Desktop/2026/Financial Enginner/KO_prices.xlsx")
print("✓ Saved to KO_prices.xlsx")