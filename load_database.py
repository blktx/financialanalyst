import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime

# ── Connect to your database ──────────────────────────────────────
# Make sure financial.db is on your Desktop
DB_PATH = "/Users/beckylin/Desktop/2026/Financial Enginner/financial.db"
conn = sqlite3.connect(DB_PATH)
print("✓ Connected to financial.db")

# ── Your 40 stocks ────────────────────────────────────────────────
GROWTH_STOCKS = [
    "TSLA", "AMD", "NVDA", "META", "PLTR",
    "MU",   "GOOGL", "MSFT", "AMZN", "CRM",
    "AAPL", "SMCI", "ARM",  "SNOW", "MSTR",
    "SHOP", "NET",  "PANW", "UBER", "SPOT",
]

DIVIDEND_STOCKS = [
    "KO",   "VZ",   "JNJ",  "PG",   "O",
    "T",    "XOM",  "ABBV", "PEP",  "MCD",
    "MMM",  "CVX",  "NEE",  "SO",   "MAIN",
    "JPM",  "BLK",  "TGT",  "WMT",  "HD",
]

# ── Load stocks table ─────────────────────────────────────────────
def load_stocks(tickers, group_type):
    print(f"\n  Loading {group_type}...")
    for ticker in tickers:
        try:
            info  = yf.Ticker(ticker).info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

            conn.execute("""
                INSERT OR REPLACE INTO stocks
                    (ticker, company, sector, price, pe_ratio, eps,
                     dividend_yield, market_cap_b, group_type, last_updated)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                ticker,
                info.get("shortName"),
                info.get("sector"),
                round(price, 2),
                round(info.get("trailingPE"), 2)       if info.get("trailingPE")     else None,
                round(info.get("trailingEps"), 2)      if info.get("trailingEps")    else None,
                round((info.get("dividendYield") or 0) * 100, 2),
                round((info.get("marketCap") or 0) / 1e9, 1),
                group_type,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ))
            conn.commit()
            print(f"    ✓ {ticker}")

        except Exception as e:
            print(f"    ✗ {ticker} failed: {e}")

# ── Load dividends table ──────────────────────────────────────────
def load_dividends(tickers):
    print(f"\n  Loading dividend history...")
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).dividends
            if hist.empty:
                print(f"    - {ticker} no dividends")
                continue

            df = hist.reset_index()
            df.columns = ["ex_date", "dividend_amount"]
            df["ticker"]  = ticker
            df["ex_date"] = df["ex_date"].dt.strftime("%Y-%m-%d")

            for _, row in df.iterrows():
                conn.execute("""
                    INSERT OR IGNORE INTO dividends (ticker, ex_date, dividend_amount)
                    VALUES (?,?,?)
                """, (row["ticker"], row["ex_date"], round(row["dividend_amount"], 4)))

            conn.commit()
            print(f"    ✓ {ticker} — {len(df)} dividend records")

        except Exception as e:
            print(f"    ✗ {ticker} failed: {e}")

# ── Load watchlist table ──────────────────────────────────────────
def load_watchlist(tickers, group_type, notes):
    for ticker in tickers:
        conn.execute("""
            INSERT OR IGNORE INTO watchlist (ticker, group_type, notes)
            VALUES (?,?,?)
        """, (ticker, group_type, notes))
    conn.commit()
    print(f"\n  ✓ Watchlist loaded for {group_type}")

# ── Run everything ────────────────────────────────────────────────
print("\n" + "=" * 45)
print("  Loading all 40 stocks into financial.db")
print("  This will take about 3-4 minutes...")
print("=" * 45)

load_stocks(GROWTH_STOCKS,   "Growth")
load_stocks(DIVIDEND_STOCKS, "Dividend")

load_dividends(DIVIDEND_STOCKS)   # dividends only matter for dividend stocks

load_watchlist(GROWTH_STOCKS,   "Growth",   "AI and growth focused")
load_watchlist(DIVIDEND_STOCKS, "Dividend", "Income and dividend focused")

conn.close()

print("\n" + "=" * 45)
print("  ALL DONE!")
print("  Open DB Browser and click Browse Data")
print("  to see your stocks table filled with data.")
print("=" * 45)
