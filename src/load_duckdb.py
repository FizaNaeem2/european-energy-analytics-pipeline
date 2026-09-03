from pathlib import Path

import duckdb


project_root = Path(__file__).resolve().parents[1]
raw_directory = project_root / "data" / "raw"

database_file = (
    project_root
    / "data"
    / "warehouse"
    / "energy_analytics.duckdb"
)

raw_files = {
    "raw_electricity_generation": (
        raw_directory
        / "electricity_generation_monthly_5_countries_2015_to_latest.json"
    ),
    "raw_electricity_demand": (
        raw_directory
        / "electricity_demand_monthly_5_countries_2015_to_latest.json"
    ),
    "raw_power_sector_emissions": (
        raw_directory
        / "power_sector_emissions_monthly_5_countries_2015_to_latest.json"
    ),
    "raw_carbon_intensity": (
        raw_directory
        / "carbon_intensity_monthly_5_countries_2015_to_latest.json"
    ),
}

select_queries = {
    "raw_electricity_generation": """
        SELECT
            item.entity,
            item.entity_code,
            item.is_aggregate_entity,
            item.date,
            item.series,
            item.is_aggregate_series,
            item.generation_twh,
            item.share_of_generation_pct
        FROM read_json_auto(?) AS response,
        UNNEST(response.data) AS records(item)
    """,
    "raw_electricity_demand": """
        SELECT
            item.entity,
            item.entity_code,
            item.is_aggregate_entity,
            item.date,
            item.demand_twh
        FROM read_json_auto(?) AS response,
        UNNEST(response.data) AS records(item)
    """,
    "raw_power_sector_emissions": """
        SELECT
            item.entity,
            item.entity_code,
            item.is_aggregate_entity,
            item.date,
            item.series,
            item.is_aggregate_series,
            item.emissions_mtco2,
            item.share_of_emissions_pct
        FROM read_json_auto(?) AS response,
        UNNEST(response.data) AS records(item)
    """,
    "raw_carbon_intensity": """
        SELECT
            item.entity,
            item.entity_code,
            item.is_aggregate_entity,
            item.date,
            item.emissions_intensity_gco2_per_kwh
        FROM read_json_auto(?) AS response,
        UNNEST(response.data) AS records(item)
    """,
}


def validate_files():
    """Confirm that every required raw file exists and is non-empty."""

    for table_name, raw_file in raw_files.items():
        if not raw_file.exists():
            raise FileNotFoundError(
                f"Missing raw file for {table_name}: {raw_file}"
            )

        if raw_file.stat().st_size == 0:
            raise ValueError(
                f"Raw file is empty for {table_name}: {raw_file}"
            )


def load_tables(connection):
    """Create or replace all four raw DuckDB tables."""

    for table_name, query in select_queries.items():
        raw_file = raw_files[table_name]

        connection.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} AS
            {query}
            """,
            [str(raw_file)],
        )

        row_count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(f"Loaded {table_name}: {row_count} rows")


def print_validation_summary(connection):
    """Print basic row-count and date-coverage checks."""

    summary = connection.execute(
        """
        SELECT
            'generation' AS dataset,
            COUNT(*) AS rows,
            COUNT(DISTINCT entity_code) AS countries,
            MIN(date) AS first_month,
            MAX(date) AS last_month
        FROM raw_electricity_generation

        UNION ALL

        SELECT
            'demand',
            COUNT(*),
            COUNT(DISTINCT entity_code),
            MIN(date),
            MAX(date)
        FROM raw_electricity_demand

        UNION ALL

        SELECT
            'emissions',
            COUNT(*),
            COUNT(DISTINCT entity_code),
            MIN(date),
            MAX(date)
        FROM raw_power_sector_emissions

        UNION ALL

        SELECT
            'carbon_intensity',
            COUNT(*),
            COUNT(DISTINCT entity_code),
            MIN(date),
            MAX(date)
        FROM raw_carbon_intensity

        ORDER BY dataset
        """
    ).fetchall()

    print("\nValidation summary:")

    for row in summary:
        print(row)


def main():
    validate_files()

    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(database_file))

    try:
        print(f"DuckDB database: {database_file}\n")
        load_tables(connection)
        print_validation_summary(connection)
    finally:
        connection.close()

    print("\nAll four raw tables loaded successfully.")


if __name__ == "__main__":
    main()