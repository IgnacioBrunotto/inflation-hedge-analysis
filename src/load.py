"""Converts raw data into tables in duckdb DB. Run from the repo root: python src/load.py"""

import duckdb 
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_DIR = PROJECT_ROOT / "data" / "warehouse.duckdb"


def load_stg_fred(con):
    """Create table with fred series, if the table exists the function replaced it"""
    con.execute(rf"""
        CREATE OR REPLACE TABLE stg_fred AS
        SELECT
                CAST(obs.date AS DATE)                         AS date,
                regexp_extract(filename, 'fred_(.+)\.json', 1) AS series_id,
                CAST(NULLIF(obs.value, '.') AS DOUBLE)         AS value
            FROM (
                SELECT filename, UNNEST(observations) AS obs
                FROM read_json('{RAW_DIR.as_posix()}/fred_*.json', filename = true)
            ) AS t
    """)


def load_stg_prices(con):
    """Create stg_fred from the raw FRED JSON files (one row per series and month)."""
    con.execute(rf"""
        CREATE OR REPLACE TABLE stg_prices AS
        SELECT
                CAST(Date AS DATE) AS date,
                regexp_extract(filename, 'prices_(.+)\.csv', 1) AS ticker,
                CAST(Open AS DOUBLE)        AS open,
                CAST(High AS DOUBLE)        AS high,
                CAST(Low AS DOUBLE)         AS low,
                CAST(Close AS DOUBLE)       AS close,
                CAST("Adj Close" AS DOUBLE) AS adj_close, 
                CAST(Volume AS BIGINT)      AS volume
        FROM read_csv('{RAW_DIR.as_posix()}/prices_*.csv', filename = true) AS t
    """)


def main():
    """Create stg_prices from the raw price CSV files (one row per ticker and day)."""

    with duckdb.connect(str(DB_DIR)) as con:
        load_stg_fred(con)
        n_fred = con.execute("SELECT COUNT(*) FROM stg_fred")
        print(f"stg_fred: {n_fred} rows. ")
        load_stg_prices(con)
        n_prices = con.execute("SELECT COUNT(*) FROM stg_prices")
        print(f"stg_prices: {n_prices} rows") 


if __name__ == "__main__":
    main()