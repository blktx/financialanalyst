# 📊 Personal Financial Dashboard — Phase 2: Streamlit Dashboard

**Built by:** Becky Lin
**GitHub:** github.com/blktx
**Background:** Cost Accountant → Financial Engineer
**Phase:** 2 of 4 — Interactive Web Dashboard
**Status:** ✅ Complete

---

## 🎯 What This Phase Delivers

A fully interactive financial research dashboard built with Python,
Streamlit, and Plotly — connected live to a local SQLite database
populated in Phase 1. No manual data entry, no copy-paste. Every
chart and table updates automatically when the database refreshes.

**Phase roadmap:**
| Phase | Focus | Status |
|---|---|---|
| 1 — Data Pipeline | Python, SQL, SQLite, automation | ✅ Complete |
| 2 — Dashboard | Streamlit, Plotly, data visualization | ✅ Complete |
| 3 — Scoring Model | Dividend quality score, alerts | 🔜 Next |
| 4 — Portfolio | GitHub, case study, resume | ⬜ Planned |

---

## 💡 Why Streamlit Over Power BI

Power BI is Windows-only. Streamlit runs anywhere Python runs —
Mac, Linux, Windows, or a cloud server. For a portfolio project,
Streamlit is actually stronger because:

- The entire dashboard is code — reviewable on GitHub
- It demonstrates Python proficiency, not just drag-and-drop
- It can be deployed publicly so anyone can view it
- It connects directly to SQLite with no export step needed

---

## 🖥️ Dashboard Pages

### 🏠 Page 1 — Overview
High-level snapshot of the entire 40-stock universe at a glance.

**What's on this page:**
- 5 KPI cards: Total Stocks, Growth, Dividend, In Uptrend, Safe Dividends
- Top 10 Growth Stocks table ranked by market cap
- Top 10 Dividend Stocks table ranked by yield
- Grouped bar chart comparing Growth vs Dividend across P/E, Yield, and Margin

**Key insight visible:** Growth stocks average P/E of 105 vs Dividend
stocks at 28.7 — confirming investors pay a 4x premium for growth.

---

### 🔍 Page 2 — Stock Screener
Live filtering across all 40 stocks with 4 interactive controls.

**Filters:**
- Group dropdown (All / Growth / Dividend)
- Sector dropdown (all sectors in database)
- Min Dividend Yield % slider (0–15%)
- Max P/E Ratio slider (0–500)

**Output:** Filtered results table + P/E vs Yield scatter plot
where bubble size = market cap. Hover any bubble to see full details.

---

### 💰 Page 3 — Dividend Dashboard
Deep dive into the 20 dividend stocks with safety analysis.

**What's on this page:**
- 4 KPI cards: Avg Yield, Avg Payout, Safe Dividends count, Avg Streak
- Horizontal bar chart of dividend yield by ticker (color-coded by intensity)
- Safety ratings table (Safe / Moderate / At Risk) with streak and payout
- Payout ratio bar chart with threshold lines at 60% and 80%

**Safety rating logic:**
| Rating | Criteria |
|---|---|
| ✅ Safe | Payout < 60% AND positive FCF AND streak ≥ 5 years |
| ⚠️ Moderate | Payout < 80% AND positive FCF |
| 🔴 At Risk | Payout > 80% OR negative FCF |

**Key finding:** Average dividend streak of 45 years across the
dividend portfolio — these are companies with multi-decade commitment
to returning cash to shareholders.

---

### 🏭 Page 4 — Sector Analysis
Concentration risk and valuation analysis by sector.

**What's on this page:**
- Pie chart: market cap distribution by sector
- Bar chart: average P/E ratio by sector
- Full sector breakdown table (count, avg P/E, avg yield, avg margin, total cap)
- Average dividend yield by sector (dividend stocks only)

**Key finding:** Technology dominates at 49.1% of total market cap —
a significant concentration. Consumer Cyclical has the highest avg
P/E at 112, driven by TSLA's 369 P/E ratio.

---

### 📈 Page 5 — Trend & Momentum
Price momentum signals and 52-week positioning.

**What's on this page:**
- 4 KPI cards: Strong Uptrend (17), Short Uptrend (3), Downtrend (13), Mixed (7)
- Price vs MA50 bar chart — green = above (bullish), red = below (bearish)
- 52-week range scatter plot — where each stock sits between its annual low and high
- Full trend signal table with MA50, MA200, and signal classification

**Signal definitions:**
| Signal | Criteria |
|---|---|
| Strong Uptrend | Price above MA50 AND above MA200 |
| Short Uptrend | Price above MA50 only |
| Downtrend | Price below both MA50 and MA200 |
| Mixed | Conflicting signals |

**Key finding as of June 2026:** 17 of 40 stocks in Strong Uptrend,
13 in Downtrend — market showing clear divergence between AI/tech
winners and defensive dividend stocks under pressure.

---

## 📸 Dashboard Screenshots

| Page | Preview |
|---|---|
| Overview | KPI cards + top 10 tables + comparison chart |
| Stock Screener | Live filters + scatter plot |
| Dividend Dashboard | Yield chart + safety ratings + payout analysis |
| Sector Analysis | Pie chart + P/E by sector |
| Trend & Momentum | MA50 bar chart + momentum signals |

*(Screenshots in `/screenshots` folder)*

---

## ⚙️ How To Run

### Install dependencies
```bash
pip3 install streamlit plotly pandas sqlite3
```

### Launch the dashboard
```bash
cd '/Users/beckylin/Desktop/2026/Financial Enginner'
streamlit run dashboard.py
```

Opens automatically at `http://localhost:8501`

### Data stays fresh automatically
The Phase 1 cron job refreshes all 40 stocks at 6pm every weekday.
The dashboard reads live from the database — just refresh the browser
page after the daily refresh runs to see updated data.

---

## 🗂️ File Structure

```
Financial Enginner/
├── dashboard.py          ← Streamlit app — 5 pages, ~350 lines
├── financial.db          ← SQLite database (Phase 1)
├── daily_refresh.py      ← Automated data refresh (Phase 1)
├── load_database.py      ← Initial data load (Phase 1)
├── add_analysis.py       ← Extended analysis columns (Phase 1)
├── stock_screener.py     ← Excel screener export (Phase 1)
├── export_analysis.py    ← Full Excel report export (Phase 1)
├── analysis_queries.sql  ← SQL queries for DB Browser (Phase 1)
├── refresh_log.txt       ← Auto-generated daily refresh log
└── screenshots/          ← Dashboard screenshots for portfolio
```

---

## 📚 Skills Demonstrated

| Skill | How It's Applied |
|---|---|
| **Streamlit** | 5-page interactive web app with sidebar navigation |
| **Plotly** | Bar charts, pie charts, scatter plots — all interactive |
| **Python** | Data loading, transformation, caching, signal logic |
| **SQL + SQLite** | Live database queries powering every page |
| **Data Visualization** | Color coding, thresholds, KPI cards, hover tooltips |
| **Financial Analysis** | Momentum signals, safety ratings, sector concentration |
| **UX Design** | Filter controls, consistent layout, insight captions |
| **Caching** | `@st.cache_data` for 1-hour refresh — performance optimization |

---

## 🔍 Key Insights From The Data (June 2026)

**Market structure:**
- NVDA leads growth at $4,969B market cap, 31.4x P/E
- Technology sector = 49.1% of total tracked market cap
- 17/40 stocks in Strong Uptrend as of last refresh

**Dividend landscape:**
- MAIN (Main Street Capital) leads yield rankings
- Average dividend streak: 45 years across dividend portfolio
- Only 6 of 20 dividend stocks rated "Safe" by payout/FCF criteria
- CVX payout ratio at 120% — flagged for monitoring

**Growth vs Dividend contrast:**
| Metric | Growth | Dividend |
|---|---|---|
| Avg Price | $333 | $189 |
| Avg P/E | 105 | 28.7 |
| Avg Yield | 0.15% | 337%* |
| Avg Margin | 18.9% | 19% |

*Yield stored as basis points in database — actual avg ~3.4%

---

## 🔜 What's Next — Phase 3: Scoring Model

Build an automated dividend quality scoring system:
- Composite score (yield + payout + streak + FCF + ROE)
- Weekly email digest with top-ranked picks
- Scenario modeling — what if yield drops 20%?
- Price alert system for watchlist stocks

Tech stack: Python, SQL window functions, smtplib

---

## 👤 About

Cost Accountant specializing in manufacturing variance analysis
(price, volume, mix) in the chemical industry. Building toward
Financial Analyst and Operational Specialist roles by combining:

- B.S. Finance Management + Information Systems
- MBA
- M.S. Computer Science (in progress)
- Hands-on data engineering and financial modeling projects

**Also building toward Power BI certification** — replicating
this dashboard in Power BI Desktop for enterprise BI skill set.

🔗 Part of a personal financial engineering portfolio.
📂 Phase 1 README: see `Phase1_README.md`
