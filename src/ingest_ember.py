import os
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.ember-energy.org/v1"

COUNTRY_CODES = ["ITA", "DEU", "FRA", "ESP", "NLD"]

START_DATE = "2015-01"

DATASETS = [
    {
        "name": "Electricity generation",
        "endpoint": "electricity-generation/monthly",
        "filename": (
            "electricity_generation_monthly_"
            "5_countries_2015_to_latest.json"
        ),
        "extra_params": {
            "is_aggregate_series": "false",
        },
    },
    {
        "name": "Electricity demand",
        "endpoint": "electricity-demand/monthly",
        "filename": (
            "electricity_demand_monthly_"
            "5_countries_2015_to_latest.json"
        ),
        "extra_params": {},
    },
    {
        "name": "Power-sector emissions",
        "endpoint": "power-sector-emissions/monthly",
        "filename": (
            "power_sector_emissions_monthly_"
            "5_countries_2015_to_latest.json"
        ),
        "extra_params": {
            "is_aggregate_series": "false",
        },
    },
    {
        "name": "Carbon intensity",
        "endpoint": "carbon-intensity/monthly",
        "filename": (
            "carbon_intensity_monthly_"
            "5_countries_2015_to_latest.json"
        ),
        "extra_params": {},
    },
]


project_root = Path(__file__).resolve().parents[1]
raw_directory = project_root / "data" / "raw"

load_dotenv(project_root / ".env")

api_key = os.getenv("EMBER_API_KEY")

if not api_key:
    raise RuntimeError(
        "EMBER_API_KEY is missing. Add it to the project .env file."
    )

raw_directory.mkdir(parents=True, exist_ok=True)


def extract_dataset(dataset):
    """Download one Ember dataset and save its unchanged JSON response."""

    url = f"{BASE_URL}/{dataset['endpoint']}"

    params = {
        "entity_code": ",".join(COUNTRY_CODES),
        "start_date": START_DATE,
        "api_key": api_key,
        **dataset["extra_params"],
    }

    print(f"\nExtracting: {dataset['name']}")

    response = requests.get(
        url,
        params=params,
        timeout=60,
    )

    print(f"HTTP status: {response.status_code}")

    if response.status_code != 200:
        print("API response:")
        print(response.text[:500])

        raise RuntimeError(
            f"Extraction failed for {dataset['name']}."
        )

    raw_file = raw_directory / dataset["filename"]

    # Preserve the exact response returned by Ember.
    raw_file.write_bytes(response.content)

    payload = response.json()
    records = payload.get("data", [])

    if not records:
        raise RuntimeError(
            f"Ember returned zero records for {dataset['name']}."
        )

    country_counts = Counter(
        record["entity_code"] for record in records
    )

    dates = [record["date"] for record in records]

    print(f"Saved: {raw_file.name}")
    print(f"Records: {len(records)}")
    print(f"Date range: {min(dates)} to {max(dates)}")
    print("Records by country:")

    for country_code in COUNTRY_CODES:
        print(
            f"  {country_code}: "
            f"{country_counts[country_code]}"
        )


def main():
    print("Starting Ember extraction pipeline...")
    print(f"Countries: {', '.join(COUNTRY_CODES)}")
    print(f"Starting date: {START_DATE}")

    for dataset in DATASETS:
        extract_dataset(dataset)

    print("\nAll four Ember datasets extracted successfully.")


if __name__ == "__main__":
    main()