with source_data as (

    select *
    from {{ source('raw', 'raw_power_sector_emissions') }}

),

standardized as (

    select
        trim(entity) as country_name,
        upper(trim(entity_code)) as country_code,
        cast(date as date) as month,
        trim(series) as energy_source,
        cast(emissions_mtco2 as double) as emissions_mtco2,
        cast(share_of_emissions_pct as double) as share_of_emissions_pct
    from source_data
    where is_aggregate_entity = false
      and is_aggregate_series = false

)

select *
from standardized