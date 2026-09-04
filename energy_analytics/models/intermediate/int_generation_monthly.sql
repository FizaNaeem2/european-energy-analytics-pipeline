with generation as (

    select *
    from {{ ref('stg_electricity_generation') }}

),

monthly_generation as (

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
                then generation_twh
                else 0
            end
        ) as renewable_generation_twh,

        sum(
            case
                when energy_source in (
                    'Coal',
                    'Gas',
                    'Other fossil'
                )
                then generation_twh
                else 0
            end
        ) as fossil_generation_twh,

        sum(
            case
                when energy_source = 'Nuclear'
                then generation_twh
                else 0
            end
        ) as nuclear_generation_twh,

        sum(
            case
                when energy_source = 'Net imports'
                then generation_twh
                else 0
            end
        ) as net_imports_twh,

        sum(
            case
                when energy_source != 'Net imports'
                then generation_twh
                else 0
            end
        ) as domestic_generation_twh,

        sum(generation_twh) as electricity_supply_twh

    from generation

    group by
        country_name,
        country_code,
        month

)

select *
from monthly_generation