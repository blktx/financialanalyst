WITH ranked_pe AS (
    SELECT
        ticker,
        sector,
        pe_ratio,
        ROW_NUMBER() OVER (
            PARTITION BY sector
            ORDER BY pe_ratio, ticker
        ) AS position_in_sector,
        COUNT(*) OVER (
            PARTITION BY sector
        ) AS sector_count
    FROM stocks
    WHERE pe_ratio > 0
)
SELECT
    sector,
    MAX(sector_count) AS sector_count,
    AVG(pe_ratio) AS sector_median_pe
FROM ranked_pe
WHERE position_in_sector IN (
    (sector_count + 1) / 2,
    (sector_count + 2) / 2
)
GROUP BY sector
ORDER BY sector;