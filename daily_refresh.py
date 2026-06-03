"""
Daily Refresh Script
Runs automatically every day to update your stock database.
Updates: prices, P/E, yield, market cap for all 40 stocks.
"""

import yfinance as yf
import sqlite3
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────
DB_PATH  = "/Users/beckylin/Desktop/2026/Financial Enginner/financial.db"
LOG_PATH = "/Users/beckylin/Desktop/2026/Financial Enginner/refresh_log.txt"

# ── Logging helper ────────────────────────────────────────────────
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{timestamp}]  {message}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

# ── Refresh one ticker ────────────────────────────────────────────
def refresh_ticker(conn, ticker):
    try:
        info  = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

        conn.execute("""
            UPDATE stocks
            SET price          = ?,
                pe_ratio       = ?,
                eps            = ?,
                dividend_yield = ?,
                market_cap_b   = ?,
                last_updated   = ?
            WHERE ticker = ?
        """, (
            round(price, 2),
            round(info.get("trailingPE"), 2)            if info.get("trailingPE")     else None,
            round(info.get("trailingEps"), 2)           if info.get("trailingEps")    else None,
            round((info.get("dividendYield") or 0) * 100, 2),
            round((info.get("marketCap") or 0) / 1e9, 1),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            ticker,
        ))
        conn.commit()
        log(f"  ✓ {ticker}  price=${price:.2f}")
        return True

    except Exception as e:
        log(f"  ✗ {ticker}  error: {e}")
        return False

# ── Refresh dividend history ──────────────────────────────────────
def refresh_dividends(conn, ticker):
    try:
        hist = yf.Ticker(ticker).dividends
        if hist.empty:
            return

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

    except Exception as e:
        log(f"  ✗ {ticker} dividends error: {e}")

# ── Main ──────────────────────────────────────────────────────────
def main():
    log("=" * 40)
    log("Daily refresh started")

    conn = sqlite3.connect(DB_PATH)

    # Get all tickers from the database
    tickers = conn.execute("SELECT ticker, group_type FROM stocks").fetchall()
    log(f"Refreshing {len(tickers)} tickers...")

    ok, fail = 0, 0
    for ticker, group_type in tickers:
        success = refresh_ticker(conn, ticker)
        if success:
            ok += 1
            # Also refresh dividends for dividend stocks
            if group_type == "Dividend":
                refresh_dividends(conn, ticker)
        else:
            fail += 1

    conn.close()
    log(f"Refresh complete — {ok} updated, {fail} failed")
    log("=" * 40)

if __name__ == "__main__":
    main()
