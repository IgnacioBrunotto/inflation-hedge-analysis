# Inflation Hedge Analysis

Which assets actually protected purchasing power against US inflation over the last two decades?

> 🚧 Work in progress

## The question

Over the last ~20 years, which asset classes (stocks, bonds, gold, cash...) delivered positive
**real** returns, and how did they behave during high- vs. low-inflation periods?

## Why it matters

"Buy X to hedge inflation" is common advice, but rarely checked with data.
This project measures real (inflation-adjusted) returns to see which claims hold up.

## Data sources

All data is pulled programmatically via API — no static datasets.

### Inflation

US Consumer Price Index for All Urban Consumers (`CPIAUCSL`, monthly, seasonally adjusted)
from the [FRED API](https://fred.stlouisfed.org/docs/api/fred/) (Federal Reserve Bank of St. Louis).

### Assets

Daily prices from Yahoo Finance via [yfinance](https://github.com/ranaroussi/yfinance).

| Asset class | Ticker | Description |
|---|---|---|
| US equities | SPY | S&P 500 index ETF |
| Long-term bonds | TLT | US Treasury bonds, 20+ years maturity |
| Inflation-linked bonds | TIP | US Treasury Inflation-Protected Securities (TIPS) |
| Gold | GLD | Physical gold ETF |
| Commodities | DBC | Diversified commodity basket ETF |
| Real estate | VNQ | US REITs ETF |
| Cash | TB3MS (FRED) | 3-month US Treasury bill rate |

### Methodology notes

- **Total returns.** All returns use adjusted close prices (dividends and coupons reinvested).
  Price-only returns would understate SPY's growth since 2006 by ~277 percentage points
  and would unfairly favour gold, which pays no income, over bonds and REITs.
- **Analysis period.** March 2006 onwards: the first full month with data for all assets
  (DBC started trading in February 2006). Data is downloaded from January 2005 so that
  year-over-year inflation is available from the start.

## Data pipeline

```
APIs (FRED, Yahoo Finance)
   │  src/ingest.py   → data/raw/                raw files, exactly as received
   ▼
   │  src/load.py     → data/warehouse.duckdb    staging tables (typed, long format)
   ▼
   │  src/validate.py → data quality checks; stops the pipeline on errors
```

Every run reloads all data from scratch. Incremental loading is not used on purpose:
adjusted prices are recalculated backwards after each dividend, and FRED revises
its series, so appending new rows to old ones would mix inconsistent versions.

## Data quality

`src/validate.py` runs 11 automated checks on the staging tables. Each check is a SQL
query that counts problem rows: **errors** stop the pipeline (exit code 1),
**warnings** are reported.

| Table | Check | Severity |
|---|---|---|
| `stg_prices` | `(date, ticker)` is unique | error |
| `stg_prices` | No nulls in `date`, `ticker`, `adj_close` | error |
| `stg_prices` | Prices are positive | error |
| `stg_prices` | All 6 tickers are present | error |
| `stg_prices` | `low <= close <= high` | warning |
| `stg_prices` | No daily move above 25% | warning |
| `stg_prices` | All tickers updated within the last 7 days | warning |
| `stg_fred` | `(date, series_id)` is unique | error |
| `stg_fred` | The only null value is CPI for October 2025 | error |
| `stg_fred` | All dates fall on the first day of the month | error |
| `stg_fred` | No missing months in any series | error |

**Known data issues**
- CPI for October 2025 was not published (US government shutdown). It is stored as
  NULL, and the check above fails if any other null appears.
- DBC started trading on 2006-02-06, so the common analysis period starts in March 2006.
- The largest single-day move in the dataset is −19.5% (VNQ, 2008-12-01), so the 25%
  threshold flags data errors such as unadjusted splits, not genuine market crashes.

## Project structure

```
├── data/
│   ├── raw/                # Data as received from the APIs (never modified)
│   ├── processed/          # Analysis outputs
│   └── warehouse.duckdb    # DuckDB database with staging tables (generated)
├── src/
│   ├── ingest.py           # Download raw data from FRED and Yahoo Finance
│   ├── load.py             # Load raw files into typed staging tables
│   └── validate.py         # Run data quality checks
├── notebooks/              # Exploratory analysis
├── dashboard/              # Power BI report
├── reports/figures/        # Charts used in this README
└── requirements.txt
```

## How to run

1. Clone the repository:
   ```
   git clone https://github.com/IgnacioBrunotto/inflation-hedge-analysis.git
   cd inflation-hedge-analysis
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/Scripts/activate   # Windows (Git Bash)
   source .venv/bin/activate       # macOS / Linux
   ```
3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
4. Get a free API key at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html),
   copy `.env.example` to `.env` and add your key.
5. Run the pipeline from the repository root:
   ```
   python src/ingest.py
   python src/load.py
   python src/validate.py
   ```

## Results

Coming soon.

