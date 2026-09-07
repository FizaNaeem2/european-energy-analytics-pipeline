from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "warehouse"
    / "energy_analytics.duckdb"
)

EXPORT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "power_bi"
)


EXPORT_QUERIES = {
    "dim_country": """
        select *
        from main_marts.dim_country
        order by country_code
    """,

    "dim_month": """
        select *
        from main_marts.dim_month
        order by month_start
    """,

    "fct_country_monthly_energy": """
        select *
        from main_marts.fct_country_monthly_energy
        order by month, country_code
    """,

    "fct_carbon_intensity_forecast": """
        select *
        from main_marts.fct_carbon_intensity_forecast
        order by month, country_code
    """
}


def export_power_bi_tables():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}"
        )

    EXPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    try:
        for table_name, query in EXPORT_QUERIES.items():

            export_data = connection.execute(
                query
            ).fetchdf()

            if export_data.empty:
                raise ValueError(
                    f"{table_name} produced no rows."
                )

            output_path = (
                EXPORT_DIRECTORY
                / f"{table_name}.csv"
            )

            export_data.to_csv(
                output_path,
                index=False,
                date_format="%Y-%m-%d"
            )

            print(
                f"Exported {table_name}: "
                f"{len(export_data):,} rows, "
                f"{len(export_data.columns)} columns"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    export_power_bi_tables()