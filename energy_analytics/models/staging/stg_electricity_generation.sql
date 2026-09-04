with source_data as (

    select *
    from {{ source('raw', 'raw_electricity_generation') }}

),

standardized as (

    select
        trim(entity) as country_name,
        upper(trim(entity_code)) as country_code,
        cast(date as date) as month,
        trim(series) as energy_source,
        cast(generation_twh as double) as generation_twh,
        cast(share_of_generation_pct as double) as share_of_generation_pct
    from source_data
    where is_aggregate_entity = false
      and is_aggregate_series = false

)

select *
from standardized