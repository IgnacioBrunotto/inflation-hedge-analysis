-- mart_asset_summary: one row per ticker with long-run results over the analysis period.
-- Key: ticker

SELECT
    ticker,
    COUNT(*)                                                        AS n_months,
    arg_max(nominal_wealth, month)                                  AS final_nominal_wealth,
    arg_max(real_wealth, month)                                     AS final_real_wealth,
    POWER(arg_max(real_wealth, month), 1.0 / (COUNT(*) / 12.0)) - 1 AS real_cagr,
    MIN(real_drawdown)                                              AS max_real_drawdown,
    arg_min(month, real_drawdown)                                   AS max_drawdown_month
FROM mart_monthly_returns
GROUP BY ticker