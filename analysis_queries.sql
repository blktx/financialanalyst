-- ============================================================
-- Extended Financial Analysis — SQL Queries
-- Run each block one at a time in DB Browser > Execute SQL
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- ANALYSIS 1: FUNDAMENTAL ANALYSIS
-- Who is actually profitable and financially healthy?
-- ────────────────────────────────────────────────────────────

-- 1A. Profitability ranking — best margins and ROE
SELECT
    ticker,
    company,
    group_type,
    sector,
    ROUND(price, 2)          AS price,
    ROUND(revenue_b, 1)      AS revenue_B,
    ROUND(profit_margin, 1)  AS profit_margin_pct,
    ROUND(roe, 1)            AS roe_pct,
    ROUND(pe_ratio, 1)       AS pe_ratio
FROM stocks
ORDER BY profit_margin DESC;


-- 1B. Financial health — debt and liquidity
-- current_ratio > 1.5 = healthy, debt_to_equity < 100 = manageable
SELECT
    ticker,
    company,
    group_type,
    ROUND(debt_to_equity, 1)  AS debt_to_equity,
    ROUND(current_ratio, 2)   AS current_ratio,
    ROUND(free_cash_flow_b, 1) AS free_cashflow_B,
    CASE
        WHEN current_ratio >= 1.5 AND debt_to_equity < 100 THEN 'Healthy'
        WHEN current_ratio >= 1.0 AND debt_to_equity < 200 THEN 'Moderate'
        ELSE 'Watch'
    END AS financial_health
FROM stocks
ORDER BY current_ratio DESC;


-- ────────────────────────────────────────────────────────────
-- ANALYSIS 2: SECTOR BREAKDOWN
-- Which sectors dominate? Where is your risk concentrated?
-- ────────────────────────────────────────────────────────────

-- 2A. Sector summary — count, avg yield, avg P/E per sector
SELECT
    sector,
    group_type,
    COUNT(*)                        AS num_stocks,
    ROUND(AVG(price), 2)            AS avg_price,
    ROUND(AVG(pe_ratio), 1)         AS avg_pe,
    ROUND(AVG(dividend_yield), 2)   AS avg_yield_pct,
    ROUND(AVG(profit_margin), 1)    AS avg_margin_pct,
    ROUND(SUM(market_cap_b), 0)     AS total_market_cap_B
FROM stocks
GROUP BY sector, group_type
ORDER BY total_market_cap_B DESC;


-- 2B. Individual stocks by sector — full sector drill-down
SELECT
    sector,
    ticker,
    company,
    group_type,
    ROUND(price, 2)           AS price,
    ROUND(market_cap_b, 1)    AS mkt_cap_B,
    ROUND(dividend_yield, 2)  AS yield_pct,
    ROUND(pe_ratio, 1)        AS pe_ratio
FROM stocks
ORDER BY sector, market_cap_b DESC;


-- ────────────────────────────────────────────────────────────
-- ANALYSIS 3: TREND ANALYSIS
-- Is the stock going up or down? Near highs or lows?
-- ────────────────────────────────────────────────────────────

-- 3A. Momentum — stocks above their 50-day moving average (bullish)
SELECT
    ticker,
    company,
    group_type,
    ROUND(price, 2)           AS price,
    ROUND(ma_50, 2)           AS ma_50,
    ROUND(ma_200, 2)          AS ma_200,
    ROUND(price_vs_ma50, 1)   AS pct_above_ma50,
    CASE
        WHEN price_vs_ma50 > 0 AND price > ma_200 THEN 'Strong Uptrend'
        WHEN price_vs_ma50 > 0                    THEN 'Short Uptrend'
        WHEN price_vs_ma50 < 0 AND price < ma_200 THEN 'Downtrend'
        ELSE 'Mixed'
    END AS trend_signal
FROM stocks
ORDER BY price_vs_ma50 DESC;


-- 3B. 52-week position — how far from highs and lows?
-- Negative price_vs_52high = how far below the peak
SELECT
    ticker,
    company,
    group_type,
    ROUND(price, 2)            AS current_price,
    ROUND(week_52_high, 2)     AS high_52wk,
    ROUND(week_52_low, 2)      AS low_52wk,
    ROUND(price_vs_52high, 1)  AS pct_from_52wk_high,
    ROUND(
        (price - week_52_low) /
        NULLIF(week_52_high - week_52_low, 0) * 100
    , 1)                       AS position_in_range_pct
FROM stocks
ORDER BY price_vs_52high DESC;


-- ────────────────────────────────────────────────────────────
-- ANALYSIS 4: DIVIDEND SAFETY SCORE
-- Is the dividend sustainable or at risk of being cut?
-- ────────────────────────────────────────────────────────────

-- 4A. Dividend safety rating
-- Safe:     payout < 60%, FCF positive, streak > 5 years
-- Moderate: payout 60-80%, FCF positive
-- At Risk:  payout > 80% or FCF negative
SELECT
    ticker,
    company,
    ROUND(price, 2)              AS price,
    ROUND(dividend_yield, 2)     AS yield_pct,
    ROUND(payout_ratio, 1)       AS payout_ratio_pct,
    ROUND(free_cash_flow_b, 2)   AS free_cashflow_B,
    dividend_streak              AS streak_years,
    CASE
        WHEN payout_ratio < 60
         AND free_cash_flow_b > 0
         AND dividend_streak >= 5  THEN '✅ Safe'
        WHEN payout_ratio < 80
         AND free_cash_flow_b > 0  THEN '⚠️  Moderate'
        WHEN payout_ratio = 0
         OR  dividend_yield = 0    THEN '➖ No Dividend'
        ELSE '🔴 At Risk'
    END AS safety_rating
FROM stocks
WHERE group_type = 'Dividend'
ORDER BY payout_ratio ASC;


-- 4B. Best dividend stocks — yield + safety combined
-- The sweet spot: high yield AND financially safe
SELECT
    ticker,
    company,
    ROUND(dividend_yield, 2)    AS yield_pct,
    ROUND(payout_ratio, 1)      AS payout_pct,
    dividend_streak             AS streak_years,
    ROUND(free_cash_flow_b, 1)  AS fcf_B,
    ROUND(roe, 1)               AS roe_pct
FROM stocks
WHERE group_type = 'Dividend'
  AND dividend_yield > 2
  AND payout_ratio < 80
  AND free_cash_flow_b > 0
ORDER BY dividend_yield DESC;
