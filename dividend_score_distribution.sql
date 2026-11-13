WITH scored_stocks AS (
    SELECT
        ticker,
        CASE
            WHEN dividend_yield IS NULL THEN NULL
            WHEN dividend_yield >= 4 THEN 5
            WHEN dividend_yield >= 2 THEN 3
            WHEN dividend_yield > 0 THEN 1
            ELSE 0
        END AS yield_score,
        CASE
            WHEN payout_ratio IS NULL THEN NULL
            WHEN payout_ratio >= 90 THEN 1
            WHEN payout_ratio >= 60 THEN 3
            WHEN payout_ratio > 0 THEN 5
            ELSE 0
        END AS payout_score
    FROM stocks
)

SELECT
    yield_score + payout_score AS total_score,
    COUNT(*) AS stock_count
FROM scored_stocks
GROUP BY yield_score + payout_score
ORDER BY total_score DESC;

