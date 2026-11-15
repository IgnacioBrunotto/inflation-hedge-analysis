-- mart_monthly_returns: one row per ticker and month with nominal and real returns,
-- cumulative wealth (value of $1 invested at the start) and real drawdown.
-- Key: (month, ticker)
-- Period: March 2006 (first full month for all assets) to the last month with CPI data.

WITH daily_ranked AS (
    SELECT
        date,
        ticker,
        adj_close,
        CAST(date_trunc('month', date) AS DATE) AS month,
        ROW_NUMBER() OVER (
            PARTITION BY ticker, date_trunc('month', date)
            ORDER BY date DESC
        ) AS rn
    FROM stg_prices
),

monthly_prices AS (
    -- Last trading day of each month
    SELECT
        month,
        ticker,
        adj_close
    FROM daily_ranked
    WHERE rn = 1
),

asset_returns AS (
    SELECT
        month,
        ticker,
        adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY month) - 1 AS nominal_return
    FROM monthly_prices
),

cash_returns AS (
    -- TB3MS is an annual rate in percent. The previous month's rate is used because it is
    -- the rate known when the month starts (avoids look-ahead bias).
    SELECT
        date AS month,
        'CASH' AS ticker,
        POWER(1 + LAG(value) OVER (ORDER BY date) / 100, 1.0 / 12) - 1 AS nominal_return
    FROM stg_fred
    WHERE series_id = 'TB3MS'
),

all_returns AS (
    SELECT month, ticker, nominal_return FROM asset_returns
    UNION ALL
    SELECT month, ticker, nominal_return FROM cash_returns
),

real_returns AS (
    SELECT
        r.month,
        r.ticker,
        r.nominal_return,
        i.monthly_inflation,
        i.yoy_inflation,
        i.regime,
        i.episode,
        i.cpi_is_imputed,
        (1 + r.nominal_return) / (1 + i.monthly_inflation) - 1 AS real_return
    FROM all_returns AS r
    INNER JOIN mart_inflation AS i
        ON r.month = i.month
    WHERE r.month >= DATE '2006-03-01'
      AND r.month <= (SELECT MAX(month) FROM mart_inflation WHERE monthly_inflation IS NOT NULL)
),

wealth AS (
    SELECT
        *,
        EXP(SUM(LN(1 + nominal_return)) OVER (
            PARTITION BY ticker
            ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )) AS nominal_wealth,
        EXP(SUM(LN(1 + real_return)) OVER (
            PARTITION BY ticker
            ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )) AS real_wealth
    FROM real_returns
)

SELECT
    month,
    ticker,
    nominal_return,
    monthly_inflation,
    yoy_inflation,
    regime,
    episode,
    cpi_is_imputed,
    real_return,
    nominal_wealth,
    real_wealth,
    -- The peak is at least 1.0: the dollar invested at the start counts as a peak.
    real_wealth / GREATEST(1.0, MAX(real_wealth) OVER (
        PARTITION BY ticker
        ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )) - 1 AS real_drawdown
FROM wealth