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

- **Inflation:** US Consumer Price Index from the [FRED API](https://fred.stlouisfed.org/docs/api/fred/) (Federal Reserve Bank of St. Louis)
- **Asset prices:** TBD

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


