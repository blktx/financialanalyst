import yfinance as yf
import pandas as pd

# ── Your two watchlists (20 each = 40 total) ─────────────────────

GROWTH_STOCKS = [
    "TSLA",   # Tesla
    "AMD",    # Advanced Micro Devices
    "NVDA",   # Nvidia
    "META",   # Meta Platforms
    "PLTR",   # Palantir (AI analytics)
    "MU",     # Micron Technology
    "GOOGL",  # Google / Alphabet
    "MSFT",   # Microsoft (AI + cloud)
    "AMZN",   # Amazon
    "CRM",    # Salesforce (AI CRM)
    "AAPL",   # Apple
    "SMCI",   # Super Micro Computer (AI servers)
    "ARM",    # ARM Holdings (AI chips)
    "SNOW",   # Snowflake (AI data cloud)
    "MSTR",   # MicroStrategy (AI + Bitcoin)
    "SHOP",   # Shopify
    "NET",    # Cloudflare (AI networking)
    "PANW",   # Palo Alto Networks (AI security)
    "UBER",   # Uber
    "SPOT",   # Spotify
]

DIVIDEND_STOCKS = [
    "KO",     # Coca-Cola
    "VZ",     # Verizon
    "JNJ",    # Johnson & Johnson
    "PG",     # Procter & Gamble
    "O",      # Realty Income (monthly dividend)
    "T",      # AT&T
    "XOM",    # Exxon Mobil
    "ABBV",   # AbbVie
    "PEP",    # PepsiCo
    "MCD",    # McDonald's
    "MMM",    # 3M
    "CVX",    # Chevron
    "NEE",    # NextEra Energy
    "SO",     # Southern Company
    "MAIN",   # Main Street Capital (monthly)
    "JPM",    # JPMorgan Chase
    "BLK",    # BlackRock
    "TGT",    # Target
    "WMT",    # Walmart
    "HD",     # Home Depot
]

# ── Pull data for one ticker ───────────────────────────────────────
def get_stock_data(ticker):
    try:
        info = yf.Ticker(ticker).info
        price     = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        div_yield = (info.get("dividendYield") or 0) * 100
        pe        = info.get("trailingPE")
        eps       = info.get("trailingEps")
        name      = info.get("shortName") or ticker
        sector    = info.get("sector") or "—"
        mkt_cap   = (info.get("marketCap") or 0) / 1e9

        return {
            "Ticker":        ticker,
            "Company":       name,
            "Sector":        sector,
            "Price ($)":     round(price, 2),
            "P/E Ratio":     round(pe, 1)  if pe  else "—",
            "EPS ($)":       round(eps, 2) if eps else "—",
            "Div Yield (%)": round(div_yield, 2),
            "Mkt Cap ($B)":  round(mkt_cap, 1),
        }
    except Exception as e:
        print(f"  Could not fetch {ticker}: {e}")
        return None

# ── Pull all tickers in a group ────────────────────────────────────
def build_table(tickers, group_name):
    print(f"\n  Fetching {group_name}...")
    rows = []
    for ticker in tickers:
        print(f"    pulling {ticker}...")
        data = get_stock_data(ticker)
        if data:
            rows.append(data)
    return pd.DataFrame(rows)

# ── Main ───────────────────────────────────────────────────────────
print("=" * 55)
print("  Stock Screener — Growth vs Dividend (40 total)")
print("=" * 55)

growth_df   = build_table(GROWTH_STOCKS,   "Growth Stocks (20)")
dividend_df = build_table(DIVIDEND_STOCKS, "Dividend Stocks (20)")

# Sort: growth by market cap, dividend by yield
growth_df   = growth_df.sort_values("Mkt Cap ($B)", ascending=False).reset_index(drop=True)
dividend_df = dividend_df.sort_values("Div Yield (%)", ascending=False).reset_index(drop=True)

# ── Print results ──────────────────────────────────────────────────
print("\n")
print("GROWTH STOCKS — sorted by market cap")
print("-" * 55)
print(growth_df[["Ticker","Company","Price ($)","P/E Ratio","EPS ($)","Mkt Cap ($B)"]].to_string(index=False))

print("\n")
print("DIVIDEND STOCKS — sorted by yield")
print("-" * 55)
print(dividend_df[["Ticker","Company","Price ($)","Div Yield (%)","P/E Ratio","EPS ($)"]].to_string(index=False))

# ── Save to Excel — two sheets in one file ─────────────────────────
output_path = "/Users/beckylin/Desktop/2026/Financial Enginner/Stock_Screener.xlsx"

with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    growth_df.to_excel(writer,   sheet_name="Growth Stocks",   index=False)
    dividend_df.to_excel(writer, sheet_name="Dividend Stocks", index=False)

print("\n")
print(f"Saved to {output_path}")
print(f"  Growth stocks:   {len(growth_df)}")
print(f"  Dividend stocks: {len(dividend_df)}")
print(f"  Total:           {len(growth_df) + len(dividend_df)}")