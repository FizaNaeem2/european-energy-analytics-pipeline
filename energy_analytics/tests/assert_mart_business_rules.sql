select
    country_code,
    month,
    demand_twh,
    carbon_intensity_gco2_per_kwh,
    renewable_share_pct,
    fossil_share_pct,
    nuclear_share_pct,
    total_emissions_mtco2

from {{ ref('fct_country_monthly_energy') }}

where
    demand_twh <= 0

    or carbon_intensity_gco2_per_kwh <= 0

    or renewable_share_pct not between 0 and 100

    or fossil_share_pct not between 0 and 100

    or nuclear_share_pct not between 0 and 100

    or abs(
        renewable_share_pct
        + fossil_share_pct
        + nuclear_share_pct
        - 100
    ) > 0.001

    or (
        total_emissions_mtco2 is not null
        and total_emissions_mtco2 < 0
    )