"""
Export data marts to CSV to use them in Power BI
"""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MARTS = [
    "mart_assets",
    "mart_inflation",
    "mart_monthly_returns",
    "mart_asset_summary",
    "mart_regime_summary",
]


def export_table(con, table_name):
    """Export a table to a CSV file in data/processed."""
    csv_path = PROCESSED_DIR / f"{table_name}.csv"
    con.execute(f"COPY {table_name} TO '{csv_path.as_posix()}' (HEADER)")
    return csv_path


def main():
    """Export all mart tables to CSV and print their row counts"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run src/transform.py first.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        for table_name in MARTS:
            csv_path = export_table(con, table_name)
            n_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"{table_name}: {n_rows} rows")
            print(f"In: {csv_path}")


if __name__ == "__main__":
    main()