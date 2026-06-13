# 📊 Personal Financial Dashboard — Phase 1: Data Pipeline

**Built by:** Becky Lin
**Background:** Cost Accountant → Financial Engineer
**Phase:** 1 of 4 — Data Pipeline
**Status:** ✅ Complete

---

## 🎯 What This Project Is

A personal financial intelligence system that automatically pulls,
stores, and analyzes stock and dividend data for 40 companies across
two investment strategies — Growth and Dividend Income.

This is Phase 1 of a 4-phase project to build a full financial
analyst dashboard, combining skills in Python, SQL, data engineering,
and financial modeling.

**Phase roadmap:**
| Phase | Focus | Status |
|---|---|---|
| 1 — Data Pipeline | Python, SQL, SQLite, automation | ✅ Complete |
| 2 — Dashboard | Streamlit, Plotly, data visualization | 🔜 Next |
| 3 — Scoring Model | Dividend quality score, alerts | ⬜ Planned |
| 4 — Portfolio | GitHub, case study, resume | ⬜ Planned |

---

## 💡 Why I Built This

As a Cost Accountant in chemical manufacturing, I perform monthly
variance analysis — breaking down price, volume, and mix to explain
margin changes. I realized these same analytical skills apply
directly to investment research.

This project bridges my accounting background with data engineering,
building toward a career as a Financial Analyst or Operational
Specialist — combining a Finance Management + Information Systems
degree, MBA, and an in-progress Master of Computer Science.

---

## 🗂️ Project Files

| File | Purpose |
|---|---|
| `stock_screener.py` | Pulls live data for 40 stocks via Yahoo Finance API |
| `load_database.py` | Initial load of all 40 stocks into SQLite database |
| `add_analysis.py` | Adds 14 extended analysis columns and populates them |
| `daily_refresh.py` | Automatically refreshes prices and dividends daily |
| `analysis_queries.sql` | 8 SQL queries across 4 analysis areas |
| `export_analysis.py` | Exports formatted 4-tab Excel analysis report |
| `financial.db` | Local SQLite database — the core data store |
| `refresh_log.txt` | Auto-generated log of every daily refresh run |

---

## 🏗️ Database Structure

Three tables work together to store and organize all data:

### stocks
The core table — one row per ticker, refreshed daily.

| Column | Type | Description |
|---|---|---|
| ticker | TEXT | Primary key (e.g. AAPL) |
| company | TEXT | Full company name |
| sector | TEXT | Industry sector |
| group_type | TEXT | Growth or Dividend |
| price | REAL | Current price |
| pe_ratio | REAL | Price to earnings ratio |
| eps | REAL | Earnings per share |
| dividend_yield | REAL | Annual yield % |
| market_cap_b | REAL | Market cap in billions |
| revenue_b | REAL | Annual revenue in billions |
| profit_margin | REAL | Net profit margin % |
| roe | REAL | Return on equity % |
| debt_to_equity | REAL | Debt to equity ratio |
| current_ratio | REAL | Liquidity ratio |
| week_52_high | REAL | 52-week high price |
| week_52_low | REAL | 52-week low price |
| ma_50 | REAL | 50-day moving average |
| ma_200 | REAL | 200-day moving average |
| price_vs_ma50 | REAL | % above/below 50-day MA |
| price_vs_52high | REAL | % below 52-week high |
| payout_ratio | REAL | % of earnings paid as dividend |
| free_cash_flow_b | REAL | Free cash flow in billions |
| dividend_streak | INTEGER | Consecutive years paying dividend |
| last_updated | TEXT | Timestamp of last refresh |

### dividends
Historical dividend payment records.

| Column | Description |
|---|---|
| ticker | Stock ticker |
| ex_date | Ex-dividend date |
| dividend_amount | Payment amount per share |

### watchlist
Master list controlling which stocks get tracked.

| Column | Description |
|---|---|
| ticker | Stock ticker |
| group_type | Growth or Dividend |
| notes | Investment thesis notes |
| added_date | Date added to watchlist |

---

## 📈 The Two Portfolios

### 🚀 Growth / AI Stocks (20 tickers)
| Ticker | Company | Focus |
|---|---|---|
| NVDA | NVIDIA | AI chips — market leader |
| MSFT | Microsoft | AI cloud + Copilot |
| GOOGL | Alphabet | AI search + infrastructure |
| AAPL | Apple | Consumer tech ecosystem |
| AMZN | Amazon | Cloud + AI services |
| TSLA | Tesla | EV + autonomous driving |
| META | Meta Platforms | Social AI + AR/VR |
| AMD | Advanced Micro Devices | AI chips competitor |
| CRM | Salesforce | AI-powered CRM |
| PLTR | Palantir | AI analytics platform |
| MU | Micron Technology | AI memory chips |
| SMCI | Super Micro Computer | AI server hardware |
| ARM | ARM Holdings | Chip architecture |
| SNOW | Snowflake | AI data cloud |
| MSTR | MicroStrategy | AI + Bitcoin strategy |
| SHOP | Shopify | AI e-commerce |
| NET | Cloudflare | AI networking security |
| PANW | Palo Alto Networks | AI cybersecurity |
| UBER | Uber | AI logistics + autonomous |
| SPOT | Spotify | AI music recommendations |

### 💰 Dividend Income Stocks (20 tickers)
| Ticker | Company | Why It's Here |
|---|---|---|
| MAIN | Main Street Capital | Monthly dividend, BDC |
| VZ | Verizon | High yield telecom |
| O | Realty Income | Monthly dividend REIT |
| T | AT&T | High yield telecom |
| PEP | PepsiCo | Dividend Aristocrat |
| CVX | Chevron | Energy dividend leader |
| TGT | Target | Dividend Aristocrat |
| KO | Coca-Cola | Dividend King 60+ years |
| JNJ | Johnson & Johnson | Dividend King |
| PG | Procter & Gamble | Dividend King |
| XOM | Exxon Mobil | Dividend Aristocrat |
| ABBV | AbbVie | High yield pharma |
| MCD | McDonald's | Dividend Aristocrat |
| MMM | 3M | Long dividend history |
| CVX | Chevron | Energy Aristocrat |
| NEE | NextEra Energy | Clean energy utility |
| SO | Southern Company | Regulated utility |
| JPM | JPMorgan Chase | Largest US bank |
| BLK | BlackRock | Asset management |
| WMT | Walmart | Retail Dividend Aristocrat |
| HD | Home Depot | Consistent dividend grower |

---

## 🔍 Analysis Areas Built

### 1. Fundamental Analysis
Measures true financial health beyond just price.

**Key metrics tracked:**
- **Profit Margin** — how much of revenue becomes profit
- **ROE (Return on Equity)** — how efficiently the company uses shareholder money
- **Debt to Equity** — how leveraged the company is
- **Current Ratio** — can it pay its short-term bills? (>1.5 = healthy)
- **Free Cash Flow** — real cash generated after expenses

```sql
-- Profitability ranking
SELECT ticker, company, group_type,
       ROUND(profit_margin, 1) AS profit_margin_pct,
       ROUND(roe, 1)           AS roe_pct,
       ROUND(debt_to_equity,1) AS debt_to_equity,
       ROUND(current_ratio, 2) AS current_ratio
FROM stocks
ORDER BY profit_margin DESC;
```

---

### 2. Sector Breakdown
Identifies concentration risk across sectors.

**Key insight:** Not all eggs in one basket — tracking how capital
is distributed across Technology, Healthcare, Energy, Financials,
Consumer Staples, Utilities, and REITs.

```sql
-- Sector summary
SELECT sector, group_type,
       COUNT(*)                      AS num_stocks,
       ROUND(AVG(pe_ratio), 1)       AS avg_pe,
       ROUND(AVG(dividend_yield), 2) AS avg_yield_pct,
       ROUND(SUM(market_cap_b), 0)   AS total_market_cap_B
FROM stocks
GROUP BY sector, group_type
ORDER BY total_market_cap_B DESC;
```

---

### 3. Trend Analysis
Identifies momentum and price positioning.

**Signals used:**
- **Price vs MA50** — above = bullish momentum, below = bearish
- **Price vs MA200** — long-term trend direction
- **52-week range position** — near highs or near lows?

| Signal | Meaning |
|---|---|
| Strong Uptrend | Above MA50 AND above MA200 |
| Short Uptrend | Above MA50 only |
| Downtrend | Below both moving averages |
| Mixed | Conflicting signals |

```sql
-- Momentum signals
SELECT ticker, company,
       ROUND(price_vs_ma50, 1) AS pct_vs_MA50,
       CASE
           WHEN price_vs_ma50 > 0 AND price > ma_200 THEN 'Strong Uptrend'
           WHEN price_vs_ma50 > 0                    THEN 'Short Uptrend'
           WHEN price_vs_ma50 < 0 AND price < ma_200 THEN 'Downtrend'
           ELSE 'Mixed'
       END AS trend_signal
FROM stocks
ORDER BY price_vs_ma50 DESC;
```

---

### 4. Dividend Safety Score
Rates each dividend stock on sustainability — is the dividend
likely to continue or at risk of being cut?

**Scoring logic:**
| Rating | Criteria |
|---|---|
| ✅ Safe | Payout < 60% AND positive FCF AND streak ≥ 5 years |
| ⚠️ Moderate | Payout < 80% AND positive FCF |
| 🔴 At Risk | Payout > 80% OR negative FCF |

```sql
-- Dividend safety rating
SELECT ticker, company,
       ROUND(dividend_yield, 2)   AS yield_pct,
       ROUND(payout_ratio, 1)     AS payout_pct,
       dividend_streak            AS streak_years,
       ROUND(free_cash_flow_b, 2) AS fcf_B,
       CASE
           WHEN payout_ratio < 60
            AND free_cash_flow_b > 0
            AND dividend_streak >= 5 THEN 'Safe'
           WHEN payout_ratio < 80
            AND free_cash_flow_b > 0 THEN 'Moderate'
           ELSE 'At Risk'
       END AS safety_rating
FROM stocks
WHERE group_type = 'Dividend'
ORDER BY payout_ratio ASC;
```

---

## ⚙️ How To Run It

### First time setup
```bash
# Install dependencies
pip3 install yfinance pandas openpyxl

# Load all 40 stocks into database
python3 load_database.py

# Add extended analysis columns
python3 add_analysis.py

# Export analysis to Excel
python3 export_analysis.py
```

### Daily use
```bash
# Refresh all prices (or let the scheduler do it automatically)
python3 daily_refresh.py
```

### Automated daily refresh (Mac)
```bash
crontab -e
# Add this line — runs at 6pm every weekday:
0 18 * * 1-5 /usr/local/bin/python3 /Users/beckylin/Desktop/daily_refresh.py
```

---

## 📊 Key Findings

**Growth vs Dividend comparison (from SQL Query 3):**

| Group | Avg Price | Avg P/E | Avg Yield |
|---|---|---|---|
| Dividend | $189 | 27.5 | 8.49% |
| Growth | $333 | 108.0 | 0.15% |

Growth stocks trade at 4x the valuation premium of dividend stocks
and pay almost no income — confirming two fundamentally different
investment strategies that require separate analysis frameworks.

---

## 📚 Skills Demonstrated

| Skill | How It's Applied |
|---|---|
| **Python** | Data ingestion, automation, error handling, OOP |
| **REST API** | Yahoo Finance via yfinance library |
| **SQL** | Schema design, INSERT, UPDATE, SELECT, GROUP BY, CASE WHEN |
| **SQLite** | Local relational database with 3 normalized tables |
| **Data Pipeline** | Automated ETL: Extract → Transform → Load |
| **Scheduling** | Cron job for daily automated refresh with logging |
| **Financial Analysis** | Fundamentals, momentum, dividend safety scoring |
| **Excel Automation** | openpyxl formatted multi-tab reports |
| **Data Modeling** | 23-column schema with normalized relationships |

---

## 🔜 What's Next — Phase 2: Dashboard

Connect this database to a **Streamlit web dashboard** featuring:
- Interactive stock screener with live filters
- Dividend safety dashboard with visual ratings
- Sector allocation charts
- Trend and momentum signals
- Insight cards summarizing top picks

Tech stack: Python, Streamlit, Plotly, SQLite

---

## 👤 About

Cost Accountant specializing in manufacturing variance analysis
(price, volume, mix) in the chemical industry. Building toward
Financial Analyst and Operational Specialist roles by combining:

- B.S. Finance Management + Information Systems
- MBA
- M.S. Computer Science (in progress)
- Hands-on data engineering and financial modeling projects

🔗 Part of a personal financial engineering portfolio.
