with demand_duplicates as (

    select
        'stg_electricity_demand' as model_name,
        country_code,
        month,
        cast(null as varchar) as energy_source,
        count(*) as duplicate_count
    from {{ ref('stg_electricity_demand') }}
    group by country_code, month
    having count(*) > 1

),

carbon_duplicates as (

    select
        'stg_carbon_intensity' as model_name,
        country_code,
        month,
        cast(null as varchar) as energy_source,
        count(*) as duplicate_count
    from {{ ref('stg_carbon_intensity') }}
    group by country_code, month
    having count(*) > 1

),

generation_duplicates as (

    select
        'stg_electricity_generation' as model_name,
        country_code,
        month,
        energy_source,
        count(*) as duplicate_count
    from {{ ref('stg_electricity_generation') }}
    group by country_code, month, energy_source
    having count(*) > 1

),

emissions_duplicates as (

    select
        'stg_power_sector_emissions' as model_name,
        country_code,
        month,
        energy_source,
        count(*) as duplicate_count
    from {{ ref('stg_power_sector_emissions') }}
    group by country_code, month, energy_source
    having count(*) > 1

)

select * from demand_duplicates
union all
select * from carbon_duplicates
union all
select * from generation_duplicates
union all
select * from emissions_duplicates