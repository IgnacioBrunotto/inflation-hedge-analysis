-- mart_regime_summary: one row per ticker and inflation regime.
-- Key: (ticker, regime)

SELECT
    ticker,
    regime,
    COUNT(*)                                            AS n_months,
    POWER(EXP(AVG(LN(1 + real_return))), 12) - 1        AS annualized_real_return,
    AVG(CASE WHEN real_return > 0 THEN 1 ELSE 0 END)    AS share_positive
FROM mart_monthly_returns
GROUP BY ticker, regime