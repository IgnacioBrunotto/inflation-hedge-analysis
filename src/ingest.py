"""Download raw data from external APIs into data/raw. Run from the repo root: python src/ingest.py"""

import requests
import json
import os
from dotenv import load_dotenv  
from pathlib import Path


FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_SERIES = ["CPIAUCSL", "TB3MS"]
START_DATE = "2005-01-01"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def fetch_fred_series(series_id, start_date, api_key):
    """Fetch observations for a FRED series and return the raw JSON response."""

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json", 
        "observation_start": start_date
    }

    response = requests.get(FRED_BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" not in content_type:
        raise ValueError(
            f"Expected JSON but received '{content_type}'  "
            f"(status {response.status_code}).  "
            f"Response starts with: {response.text[:200]} "
        )
    
    return response.json()


def save_raw_json(data, path):
    """Save a dictionary as a JSON file, creating parent folders if needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,"w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    load_dotenv()
    
    api_key = os.getenv("FRED_API_KEY")

    if api_key is None:
        raise ValueError("FRED_API_KEY not found.")

    for series_id in FRED_SERIES:
        series_data = fetch_fred_series(series_id, START_DATE, api_key)
        file_path = RAW_DIR / f"fred_{series_id}.json"
        save_raw_json(series_data, file_path)
        print(
            f"Series saved: {series_id}, "
            f"Observations: {len(series_data['observations'])}, "
            f"In: {file_path} "
        )

if __name__ == "__main__":
    main()