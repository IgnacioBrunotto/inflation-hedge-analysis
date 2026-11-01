"""Run data quality checks on the staging tables. Run from the repo root: python src/validate.py"""

from pathlib import Path
import sys

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"

CHECKS = [
    {
        "name": "stg_prices: (date, ticker) is unique",
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