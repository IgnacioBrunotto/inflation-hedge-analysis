-- mart_inflation: one row per month with the CPI level, inflation rates and inflation regime.
-- Key: month
-- CPI for 2025-10 was not published (US government shutdown); it is filled with the
-- geometric mean of the neighbouring months, which preserves the Sep -> Nov inflation.

WITH cpi_filled AS (
    SELECT
        date AS month,
        CASE
            WHEN value IS NULL
                THEN SQRT(LAG(value) OVER (ORDER BY date) * LEAD(value) OVER (ORDER BY date))
            ELSE value
        END AS cpi,
        value IS NULL AS cpi_is_imputed
    FROM stg_fred
    WHERE series_id = 'CPIAUCSL'
),

inflation AS (
    SELECT
        month,
        cpi,
        cpi_is_imputed,
        cpi / LAG(cpi) OVER (ORDER BY month) - 1      AS monthly_inflation,
        cpi / LAG(cpi, 12) OVER (ORDER BY month) - 1  AS yoy_inflation
    FROM cpi_filled
)

SELECT
    month,
    cpi,
    cpi_is_imputed,
    monthly_inflation,
    yoy_inflation,
    CASE
        WHEN yoy_inflation >= 0.04 THEN 'high'
        WHEN yoy_inflation > 0.02 THEN 'moderate'
        WHEN yoy_inflation <= 0.02 THEN 'low'
    END AS regime
FROM inflation