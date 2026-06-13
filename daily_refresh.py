"""
Daily Refresh Script — Full Extended Version
Runs automatically every day to update your stock database.
Updates ALL columns including extended analysis data.

Run manually: python3 daily_refresh.py
Scheduled:    cron runs this at 6pm every weekday automatically
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

# ── Refresh one ticker — ALL columns ─────────────────────────────
def refresh_ticker(conn, ticker, group_type):
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

        # ── Basic ──────────────────────────────────────────────
        pe_ratio      = info.get("trailingPE")
        eps           = info.get("trailingEps")
        div_yield     = (info.get("dividendYield") or 0) * 100
        market_cap_b  = (info.get("marketCap") or 0) / 1e9

        # ── Fundamentals ───────────────────────────────────────
        revenue_b     = (info.get("totalRevenue") or 0) / 1e9
        profit_margin = (info.get("profitMargins") or 0) * 100
        roe           = (info.get("returnOnEquity") or 0) * 100
        debt_to_eq    = info.get("debtToEquity")
        current_ratio = info.get("currentRatio")
        fcf           = (info.get("freeCashflow") or 0) / 1e9
        payout_ratio  = (info.get("payoutRatio") or 0) * 100

        # ── Trend / momentum ───────────────────────────────────
        week_52_high  = info.get("fiftyTwoWeekHigh")
        week_52_low   = info.get("fiftyTwoWeekLow")
        ma_50         = info.get("fiftyDayAverage")
        ma_200        = info.get("twoHundredDayAverage")
        price_vs_ma50 = round((price - ma_50) / ma_50 * 100, 2)             if ma_50         else None
        price_vs_52h  = round((price - week_52_high) / week_52_high * 100, 2) if week_52_high else None

        # ── Dividend streak ────────────────────────────────────
        hist = stock.dividends
        if not hist.empty:
            years        = set(hist.index.year)
            current_year = datetime.now().year
            streak       = 0
            for yr in range(current_year, current_year - 60, -1):
                if yr in years:
                    streak += 1
                else:
                    break
        else:
            streak = 0

        # ── Update ALL columns in one query ────────────────────
        conn.execute("""
            UPDATE stocks SET
                price            = ?,
                pe_ratio         = ?,
                eps              = ?,
                dividend_yield   = ?,
                market_cap_b     = ?,
                revenue_b        = ?,
                profit_margin    = ?,
                roe              = ?,
                debt_to_equity   = ?,
                current_ratio    = ?,
                free_cash_flow_b = ?,
                payout_ratio     = ?,
                week_52_high     = ?,
                week_52_low      = ?,
                ma_50            = ?,
                ma_200           = ?,
                price_vs_ma50    = ?,
                price_vs_52high  = ?,
                dividend_streak  = ?,
                last_updated     = ?
            WHERE ticker = ?
        """, (
            round(price, 2),
            round(pe_ratio, 2)      if pe_ratio      else None,
            round(eps, 2)           if eps           else None,
            round(div_yield, 2),
            round(market_cap_b, 1),
            round(revenue_b, 2),
            round(profit_margin, 2),
            round(roe, 2),
            round(debt_to_eq, 2)    if debt_to_eq    else None,
            round(current_ratio, 2) if current_ratio else None,
            round(fcf, 2),
            round(payout_ratio, 2),
            week_52_high,
            week_52_low,
            round(ma_50, 2)         if ma_50         else None,
            round(ma_200, 2)        if ma_200        else None,
            price_vs_ma50,
            price_vs_52h,
            streak,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            ticker,
        ))
        conn.commit()

        log(f"  ✓ {ticker:6s}  ${price:.2f}  margin={profit_margin:.1f}%  yield={div_yield:.2f}%  streak={streak}yr")
        return True

    except Exception as e:
        log(f"  ✗ {ticker}  error: {e}")
        return False

# ── Refresh dividend history ───────────────────────────────────────
def refresh_dividends(conn, ticker):
    try:
        hist = yf.Ticker(ticker).dividends
        if hist.empty:
            return 0

        df = hist.reset_index()
        df.columns   = ["ex_date", "dividend_amount"]
        df["ticker"]  = ticker
        df["ex_date"] = df["ex_date"].dt.strftime("%Y-%m-%d")

        rows_before = conn.execute(
            "SELECT COUNT(*) FROM dividends WHERE ticker = ?", (ticker,)
        ).fetchone()[0]

        for _, row in df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO dividends (ticker, ex_date, dividend_amount)
                VALUES (?,?,?)
            """, (row["ticker"], row["ex_date"], round(row["dividend_amount"], 4)))
        conn.commit()

        rows_after = conn.execute(
            "SELECT COUNT(*) FROM dividends WHERE ticker = ?", (ticker,)
        ).fetchone()[0]
        new_rows = rows_after - rows_before
        if new_rows > 0:
            log(f"    💰 {ticker}  +{new_rows} new dividend records")
        return new_rows

    except Exception as e:
        log(f"  ✗ {ticker} dividends error: {e}")
        return 0

# ── Main ───────────────────────────────────────────────────────────
def main():
    log("=" * 50)
    log("Daily refresh started — Full Extended Version")
    log("=" * 50)

    conn = sqlite3.connect(DB_PATH)

    tickers = conn.execute(
        "SELECT ticker, group_type FROM stocks ORDER BY ticker"
    ).fetchall()
    log(f"Refreshing {len(tickers)} tickers (all columns)...\n")

    ok, fail = 0, 0
    for ticker, group_type in tickers:
        success = refresh_ticker(conn, ticker, group_type)
        if success:
            ok += 1
            if group_type == "Dividend":
                refresh_dividends(conn, ticker)
        else:
            fail += 1

    conn.close()

    log(f"\n{'=' * 50}")
    log(f"Refresh complete — {ok} updated, {fail} failed")
    log(f"{'=' * 50}\n")

if __name__ == "__main__":
    main()
