"""Build analysis tables (marts) from the staging tables.

Each table is defined in sql/<table_name>.sql.
Run from the repo root: python src/transform.py
"""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
SQL_DIR = PROJECT_ROOT / "sql"

# Order matters: each table can only read from tables built before it.
MARTS = [
    "mart_inflation",
    "mart_monthly_returns",
    "mart_asset_summary",
    "mart_regime_summary",
]


def build_table(con, table_name):
    """Create or replace a table from the query in sql/<table_name>.sql."""
    query = (SQL_DIR / f"{table_name}.sql").read_text(encoding="utf-8")
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS {query}")


def main():
    """Build all mart tables in order and print their row counts."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run src/load.py first.")

    with duckdb.connect(str(DB_PATH)) as con:
        for table_name in MARTS:
            build_table(con, table_name)
            n_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"{table_name}: {n_rows} rows")


if __name__ == "__main__":
    main()