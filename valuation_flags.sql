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
),
sector_medians AS (
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
)
SELECT
    s.ticker,
    s.sector,
    s.pe_ratio,
    m.sector_count,
    m.sector_median_pe,
    CASE
        WHEN s.pe_ratio IS NULL OR s.pe_ratio <= 0
            THEN 'P/E unavailable'
        WHEN m.sector_median_pe IS NULL
            THEN 'Sector median unavailable'
        WHEN m.sector_count < 2
            THEN 'Insufficient peers'
        WHEN s.pe_ratio < m.sector_median_pe
            THEN 'Below sector median'
        WHEN s.pe_ratio > m.sector_median_pe
            THEN 'Above sector median'
        ELSE 'At sector median'
    END AS valuation_flag
FROM stocks AS s
LEFT JOIN sector_medians AS m
    ON s.sector = m.sector
ORDER BY s.sector, s.pe_ratio, s.ticker;