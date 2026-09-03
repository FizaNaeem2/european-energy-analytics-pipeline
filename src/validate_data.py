from pathlib import Path

import duckdb


EXPECTED_COUNTRIES = {"ITA", "DEU", "FRA", "ESP", "NLD"}

TABLE_CONFIG = {
    "raw_electricity_generation": {
        "key_columns": ["entity_code", "date", "series"],
        "required_columns": ["entity", "entity_code", "date", "series"],
        "metrics": ["generation_twh", "share_of_generation_pct"],
    },
    "raw_electricity_demand": {
        "key_columns": ["entity_code", "date"],
        "required_columns": ["entity", "entity_code", "date"],
        "metrics": ["demand_twh"],
    },
    "raw_power_sector_emissions": {
        "key_columns": ["entity_code", "date", "series"],
        "required_columns": ["entity", "entity_code", "date", "series"],
        "metrics": ["emissions_mtco2", "share_of_emissions_pct"],
    },
    "raw_carbon_intensity": {
        "key_columns": ["entity_code", "date"],
        "required_columns": ["entity", "entity_code", "date"],
        "metrics": ["emissions_intensity_gco2_per_kwh"],
    },
}


project_root = Path(__file__).resolve().parents[1]

database_file = (
    project_root
    / "data"
    / "warehouse"
    / "energy_analytics.duckdb"
)

if not database_file.exists():
    raise FileNotFoundError(f"DuckDB database not found: {database_file}")


def count_duplicate_groups(connection, table_name, key_columns):
    keys = ", ".join(key_columns)

    query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT {keys}, COUNT(*) AS occurrences
            FROM {table_name}
            GROUP BY {keys}
            HAVING COUNT(*) > 1
        )
    """

    return connection.execute(query).fetchone()[0]


def count_nulls(connection, table_name, column_name):
    query = f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE {column_name} IS NULL
    """

    return connection.execute(query).fetchone()[0]


def get_countries(connection, table_name):
    rows = connection.execute(
        f"""
        SELECT DISTINCT entity_code
        FROM {table_name}
        ORDER BY entity_code
        """
    ).fetchall()

    return {row[0] for row in rows}


def validate_table(connection, table_name, config):
    print(f"\nValidating: {table_name}")

    row_count = connection.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    print(f"  Rows: {row_count}")

    duplicate_groups = count_duplicate_groups(
        connection,
        table_name,
        config["key_columns"],
    )

    print(f"  Duplicate key groups: {duplicate_groups}")

    for column in config["required_columns"]:
        null_count = count_nulls(
            connection,
            table_name,
            column,
        )

        print(f"  Null {column}: {null_count}")

    countries = get_countries(connection, table_name)

    missing_countries = EXPECTED_COUNTRIES - countries
    unexpected_countries = countries - EXPECTED_COUNTRIES

    print(f"  Countries: {sorted(countries)}")
    print(f"  Missing countries: {sorted(missing_countries)}")
    print(f"  Unexpected countries: {sorted(unexpected_countries)}")

    for metric in config["metrics"]:
        null_count, minimum, maximum = connection.execute(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE {metric} IS NULL),
                MIN({metric}),
                MAX({metric})
            FROM {table_name}
            """
        ).fetchone()

        print(
            f"  Metric {metric}: "
            f"nulls={null_count}, min={minimum}, max={maximum}"
        )

    coverage = connection.execute(
        f"""
        SELECT
            entity_code,
            MIN(date),
            MAX(date),
            COUNT(DISTINCT date)
        FROM {table_name}
        GROUP BY entity_code
        ORDER BY entity_code
        """
    ).fetchall()

    print("  Monthly coverage:")

    for row in coverage:
        print(f"    {row}")


def main():
    connection = duckdb.connect(str(database_file), read_only=True)

    try:
        for table_name, config in TABLE_CONFIG.items():
            validate_table(
                connection,
                table_name,
                config,
            )
    finally:
        connection.close()

    print("\nData-quality inspection completed.")


if __name__ == "__main__":
    main()