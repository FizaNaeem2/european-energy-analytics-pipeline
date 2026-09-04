with emissions as (

    select *
    from {{ ref('stg_power_sector_emissions') }}

),

monthly_emissions as (

    select
        country_name,
        country_code,
        month,

        sum(
            case
                when energy_source in (
                    'Bioenergy',
                    'Hydro',
                    'Other renewables',
                    'Solar',
                    'Wind'
                )
                then emissions_mtco2
                else 0
            end
        ) as renewable_emissions_mtco2,

        sum(
            case
                when energy_source in (
                    'Coal',
                    'Gas',
                    'Other fossil'
                )
                then emissions_mtco2
                else 0
            end
        ) as fossil_emissions_mtco2,

        sum(
            case
                when energy_source = 'Nuclear'
                then emissions_mtco2
                else 0
            end
        ) as nuclear_emissions_mtco2,

        sum(emissions_mtco2) as total_emissions_mtco2

    from emissions

    group by
        country_name,
        country_code,
        month

)

select *
from monthly_emissions