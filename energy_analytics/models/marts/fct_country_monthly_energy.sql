with demand as (

    select *
    from {{ ref('stg_electricity_demand') }}

),

generation as (

    select *
    from {{ ref('int_generation_monthly') }}

),

emissions as (

    select *
    from {{ ref('int_emissions_monthly') }}

),

carbon_intensity as (

    select *
    from {{ ref('stg_carbon_intensity') }}

),

combined as (

    select
        demand.country_name,
        demand.country_code,
        demand.month,

        demand.demand_twh,

        generation.renewable_generation_twh,
        generation.fossil_generation_twh,
        generation.nuclear_generation_twh,
        generation.net_imports_twh,
        generation.domestic_generation_twh,
        generation.electricity_supply_twh,

        emissions.renewable_emissions_mtco2,
        emissions.fossil_emissions_mtco2,
        emissions.nuclear_emissions_mtco2,
        emissions.total_emissions_mtco2,

        carbon_intensity.carbon_intensity_gco2_per_kwh,

        100.0
        * generation.renewable_generation_twh
        / nullif(generation.domestic_generation_twh, 0)
            as renewable_share_pct,

        100.0
        * generation.fossil_generation_twh
        / nullif(generation.domestic_generation_twh, 0)
            as fossil_share_pct,

        100.0
        * generation.nuclear_generation_twh
        / nullif(generation.domestic_generation_twh, 0)
            as nuclear_share_pct,

        100.0
        * generation.net_imports_twh
        / nullif(demand.demand_twh, 0)
            as net_import_dependence_pct,

        generation.electricity_supply_twh
        - demand.demand_twh
            as supply_demand_gap_twh

    from demand

    left join generation
        on demand.country_code = generation.country_code
        and demand.month = generation.month

    left join emissions
        on demand.country_code = emissions.country_code
        and demand.month = emissions.month

    left join carbon_intensity
        on demand.country_code = carbon_intensity.country_code
        and demand.month = carbon_intensity.month

)

select *
from combined