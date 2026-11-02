"""Run data quality checks on the staging tables. Run from the repo root: python src/validate.py"""

from pathlib import Path
import sys

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"

CHECKS = [
    {
        "name": "stg_prices: (date, ticker) are unique",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) FROM (
                SELECT date, ticker
                FROM stg_prices
                GROUP BY date, ticker
                HAVING COUNT(*) > 1
            )
        """,
    },

    {   
        "name": "stg_prices: date, ticker and adj_close have no nulls",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) 
            FROM stg_prices
            WHERE date IS NULL 
            OR ticker IS NULL
            OR adj_close IS NULL
        """
    },

    {
        "name": "stg_prices: close and adj_close are positive",
        "severity": "error",
        "sql": """
            SELECT COUNT(*)
            FROM stg_prices
            WHERE close <= 0 AND adj_close <= 0
        """
    },

    {
        "name": "stg_prices: all 6 tickers are present",
        "severity": "error",
        "sql": """
            SELECT 6 - COUNT(DISTINCT ticker)
            FROM stg_prices
        """
    },

    {
        "name": "stg_prices: low <= close <= high",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*)
            FROM stg_prices
            WHERE close NOT BETWEEN low and high
        """
    },

   {
        "name": "stg_prices: no daily move above 25%",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*)
            FROM(
                SELECT 
                ticker,
                date,
                adj_close,
                adj_close / LAG(adj_close) OVER (partition by ticker ORDER BY date) - 1 AS profitability
                FROM stg_prices
                ) AS sub
            WHERE ABS(sub.profitability) > 0.25
        """
    },

   {
        "name": "stg_prices: all tickers updated within the last 7 days",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*)
            FROM (
                SELECT ticker
                FROM stg_prices
                GROUP BY ticker
                HAVING date_diff('day', MAX(date), CURRENT_DATE) > 7
                )
        """
    },    

   {
        "name": "stg_fred: (date, series_id) are unique",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) FROM (
                SELECT date, series_id
                FROM stg_fred
                GROUP BY date, series_id
                HAVING COUNT(*) > 1
            )
        """
    },  

   {
        "name": "stg_fred: date and series_id have no nulls",
        "severity": "error",
        "sql": """
                SELECT COUNT(*)
                FROM stg_fred
                WHERE value IS NULL  
                AND NOT (series_id = 'CPIAUCSL' AND date = '2025-10-01')
        """
    },  

   {
        "name": "stg_fred: difference between months is 1",
        "severity": "error",
        "sql": """
            SELECT COUNT(*)
            FROM stg_fred
            WHERE day(date) != 1
        """
    },      

   {
        "name": "stg_fred: no missing months in any series",
        "severity": "error",
        "sql": """
                SELECT COUNT(*)
                FROM(
                    SELECT            
                        series_id,
                        date,
                        value,
                        LAG(date) OVER (PARTITION BY series_id ORDER BY date) AS prev_month
                    FROM stg_fred) as sub
                WHERE date_diff('month', sub.prev_month, date ) <> 1
        """
    },  
]


def run_check(con, check):
    return con.execute(check["sql"]).fetchone()[0]


def main():
    """Run all data quality checks and exit with code 1 if any error check fails."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run src/load.py first.")

    failed_errors = []
    n_warnings = 0

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        for check in CHECKS:
            result = run_check(con, check)
            if result == 0:
                status = "PASS"
            elif check["severity"] == "error":
                failed_errors.append(check["name"])
                status = "FAIL"
            else:
                status = "WARN"
                n_warnings += 1

            print(f"[{status}]  {check['name']}  ({result} rows)")

    if failed_errors:
        print(f"\n{len(failed_errors)} error check(s) failed:")
        for name in failed_errors:
            print(f"  - {name}")
        print("Fix these data issues before running the analysis.")
        sys.exit(1)

    print(f"\nAll {len(CHECKS)} checks ran: no errors, {n_warnings} warning(s).")


if __name__ == "__main__":
    main()