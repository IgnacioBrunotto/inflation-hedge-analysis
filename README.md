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

![Real value of $1 invested in each asset since March 2006](reports\figures\real_wealth.png)

### Findings: long-run real wealth (March 2006 – September 2026)

- **Only stocks and gold multiplied purchasing power.** $1 invested in SPY grew to ×5.15
  in real terms, and in GLD to ×4.03. Real estate (VNQ) roughly doubled (×1.93).
- **Three assets ended near or below their starting purchasing power:** inflation-linked
  bonds (TIP ×1.13) and commodities (DBC ×1.04) barely beat inflation, while long-term
  bonds (TLT ×0.98) and cash (×0.83) lost purchasing power over 20 years.
- **Commodities behave like insurance.** DBC protected purchasing power during the
  high-inflation episodes, but over the whole period it created almost no real wealth:
  the protection came at a high cost the rest of the time.
- **The path matters as much as the destination.** VNQ fell about 70% from its peak by
  early 2009, during the housing and financial crisis, and needed years to recover.



  ![Cumulative real return of each asset in the 2008 and 2021–23 high-inflation episodes](reports\figures\episode_returns.png)

  ### Findings: high-inflation episodes

- **Commodities (DBC) were the only asset with positive real returns in both episodes**
  (+8.8% in 2008 and +16.7% in 2021–23).
- **Gold (GLD) roughly preserved purchasing power** (+3.4% and −0.4%): it neither gained
  nor lost much.
- **Long-term bonds behaved very differently in each episode.** TLT gained +5.1% in 2008 but
  lost −30.4% in 2021–23, consistent with the sharp rise in interest rates in 2022: when rates
  rise, the price of existing long-term bonds falls. Inflation-linked bonds (TIP) also lost −15.7%.
- **Stocks (SPY) and real estate (VNQ) lost in both episodes.** SPY's −26.8% in 2008 overlaps
  with the start of the financial crisis; in 2021–23 its loss was much smaller (−5.1%).
- **Cash lost purchasing power in both episodes** (−2.5% and −9.5%).



![Real annual return vs. worst real drawdown for each asset](reports\figures\return_vs_drawdown.png)

### Findings: return vs. risk

- **The best real returns came with large drawdowns.** SPY earned about 8.3% per year in
  real terms and GLD about 7.0%, but at their worst they lost 52% and 46% of their real value.
- **Larger drawdowns were not rewarded with higher returns.** The two assets with the deepest
  drawdowns, DBC (−78%) and VNQ (−70%), delivered only about 0.2% and 3.2% per year.
- **Lower-risk assets barely kept up with inflation.** TIP and cash had the smallest
  drawdowns (about −22% and −24%), but returned about 0.6% and −0.9% per year.
- **Conclusion:** taking more risk did not guarantee more return, and no asset delivered
  strong real returns without deep drawdowns along the way.