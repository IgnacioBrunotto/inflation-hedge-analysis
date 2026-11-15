-- mart_assets: one row per asset with descriptive attributes for reporting.
-- Key: ticker
-- sort_order follows asset class (growth assets first, cash last), not results,
-- so it does not change when the data is refreshed.

SELECT
    ticker,
    asset_class,
    description,
    sort_order,
    color_hex
FROM (
    VALUES
        ('SPY',  'US equities',            'S&P 500 index ETF',                                  1, '#2a78d6'),
        ('VNQ',  'Real estate',            'US REITs ETF',                                       2, '#eda100'),
        ('DBC',  'Commodities',            'Diversified commodity basket ETF',                   3, '#1baf7a'),
        ('GLD',  'Gold',                   'Physical gold ETF',                                  4, '#eb6834'),
        ('TLT',  'Long-term bonds',        'US Treasury bonds, 20+ years maturity',              5, '#008300'),
        ('TIP',  'Inflation-linked bonds', 'US Treasury Inflation-Protected Securities (TIPS)',  6, '#e87ba4'),
        ('CASH', 'Cash',                   '3-month US Treasury bill rate (FRED TB3MS)',         7, '#6250d6')
) AS assets (ticker, asset_class, description, sort_order, color_hex)