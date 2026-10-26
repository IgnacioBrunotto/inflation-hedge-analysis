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

### Asset prices

Daily prices from Yahoo Finance via [yfinance](https://github.com/ranaroussi/yfinance).
All returns use adjusted close prices (total return, dividends reinvested).

| Asset class | Ticker | Description |
|---|---|---|
| US equities | SPY | S&P 500 index ETF |
| Long-term bonds | TLT | US Treasury bonds, 20+ years maturity |
| Inflation-linked bonds | TIP | US Treasury Inflation-Protected Securities (TIPS) |
| Gold | GLD | Physical gold ETF |
| Commodities | DBC | Diversified commodity basket ETF |
| Real estate | VNQ | US REITs ETF |
| Cash | TB3MS (FRED) | 3-month US Treasury bill rate |

### Inflation

US Consumer Price Index for All Urban Consumers (`CPIAUCSL`, monthly, seasonally adjusted)
from the [FRED API](https://fred.stlouisfed.org/docs/api/fred/).

**Analysis period:** March 2006 onwards — the first full month with data for all assets
(DBC started trading in February 2006).

Data is pulled programmatically via API — no static datasets.

## Project structure

```
├── data/
│   ├── raw/          # Data as received from the APIs (never modified)
│   └── processed/    # Cleaned and transformed data
├── src/              # Reusable code: ingestion and transformation
├── notebooks/        # Exploratory analysis
├── dashboard/        # Power BI report
├── reports/figures/  # Charts used in this README
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
4. Get a free API key at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html), copy `.env.example` to `.env` and add your key.

## Results


