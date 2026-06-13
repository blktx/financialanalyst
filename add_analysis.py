"""
Phase 1 Extended Analysis
Adds fundamental, trend, sector, and dividend safety data
to your existing financial.db database.

Run once — then use the SQL queries and Excel export scripts.
"""

import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "/Users/beckylin/Desktop/2026/Financial Enginner/financial.db"
conn = sqlite3.connect(DB_PATH)
print("✓ Connected to financial.db")

# ── Step 1: Add new columns to stocks table ───────────────────────
print("\nAdding new columns to stocks table...")

new_columns = [
    # Fundamental analysis
    ("revenue_b",        "REAL"),   # Total revenue in billions
    ("profit_margin",    "REAL"),   # Net profit margin %
    ("roe",              "REAL"),   # Return on equity %
    ("debt_to_equity",   "REAL"),   # Debt to equity ratio
    ("current_ratio",    "REAL"),   # Current assets / current liabilities
    # Trend analysis
    ("week_52_high",     "REAL"),   # 52-week high price
    ("week_52_low",      "REAL"),   # 52-week low price
    ("ma_50",            "REAL"),   # 50-day moving average
    ("ma_200",           "REAL"),   # 200-day moving average
    ("price_vs_ma50",    "REAL"),   # % above or below 50-day MA
    ("price_vs_52high",  "REAL"),   # % below 52-week high
    # Dividend safety
    ("payout_ratio",     "REAL"),   # % of earnings paid as dividend
    ("free_cash_flow_b", "REAL"),   # Free cash flow in billions
    ("dividend_streak",  "INTEGER"),# Consecutive years paying dividend
]

for col_name, col_type in new_columns:
    try:
        conn.execute(f"ALTER TABLE stocks ADD COLUMN {col_name} {col_type}")
        print(f"  ✓ Added column: {col_name}")
    except Exception:
        print(f"  - Column already exists: {col_name}")

conn.commit()

# ── Step 2: Pull extended data for each ticker ────────────────────
print("\nPulling extended data for all 40 tickers...")
print("This will take about 4-5 minutes...\n")

tickers = conn.execute("SELECT ticker FROM stocks").fetchall()
tickers = [t[0] for t in tickers]

ok, fail = 0, 0

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # ── Fundamentals ──────────────────────────────────────────
        revenue      = (info.get("totalRevenue") or 0) / 1e9
        profit_margin = (info.get("profitMargins") or 0) * 100
        roe           = (info.get("returnOnEquity") or 0) * 100
        debt_to_eq    = info.get("debtToEquity")
        current_ratio = info.get("currentRatio")

        # ── Trend / momentum ─────────────────────────────────────
        week_52_high  = info.get("fiftyTwoWeekHigh")
        week_52_low   = info.get("fiftyTwoWeekLow")
        ma_50         = info.get("fiftyDayAverage")
        ma_200        = info.get("twoHundredDayAverage")
        price         = info.get("currentPrice") or info.get("regularMarketPrice") or 0

        price_vs_ma50   = round((price - ma_50)  / ma_50  * 100, 2) if ma_50   else None
        price_vs_52high = round((price - week_52_high) / week_52_high * 100, 2) if week_52_high else None

        # ── Dividend safety ───────────────────────────────────────
        payout_ratio    = (info.get("payoutRatio") or 0) * 100
        fcf             = (info.get("freeCashflow") or 0) / 1e9

        # Dividend streak — count consecutive years with payments
        hist = stock.dividends
        if not hist.empty:
            years = set(hist.index.year)
            current_year = datetime.now().year
            streak = 0
            for yr in range(current_year, current_year - 60, -1):
                if yr in years:
                    streak += 1
                else:
                    break
        else:
            streak = 0

        # ── Update database ───────────────────────────────────────
        conn.execute("""
            UPDATE stocks SET
                revenue_b        = ?,
                profit_margin    = ?,
                roe              = ?,
                debt_to_equity   = ?,
                current_ratio    = ?,
                week_52_high     = ?,
                week_52_low      = ?,
                ma_50            = ?,
                ma_200           = ?,
                price_vs_ma50    = ?,
                price_vs_52high  = ?,
                payout_ratio     = ?,
                free_cash_flow_b = ?,
                dividend_streak  = ?
            WHERE ticker = ?
        """, (
            round(revenue, 2),
            round(profit_margin, 2),
            round(roe, 2),
            round(debt_to_eq, 2)    if debt_to_eq    else None,
            round(current_ratio, 2) if current_ratio else None,
            week_52_high,
            week_52_low,
            round(ma_50, 2)         if ma_50   else None,
            round(ma_200, 2)        if ma_200  else None,
            price_vs_ma50,
            price_vs_52high,
            round(payout_ratio, 2),
            round(fcf, 2),
            streak,
            ticker,
        ))
        conn.commit()
        print(f"  ✓ {ticker:6s}  margin={profit_margin:.1f}%  ROE={roe:.1f}%  streak={streak}yr")
        ok += 1

    except Exception as e:
        print(f"  ✗ {ticker} failed: {e}")
        fail += 1

conn.close()
print(f"\n{'='*45}")
print(f"  Done! {ok} updated, {fail} failed")
print(f"  Now run the SQL queries in DB Browser")
print(f"  or run the Excel export script next.")
print(f"{'='*45}")
