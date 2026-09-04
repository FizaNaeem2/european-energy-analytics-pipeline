with source_data as (

    select *
    from {{ source('raw', 'raw_carbon_intensity') }}

),

standardized as (

    select
        trim(entity) as country_name,
        upper(trim(entity_code)) as country_code,
        cast(date as date) as month,
        cast(emissions_intensity_gco2_per_kwh as double)
            as carbon_intensity_gco2_per_kwh
    from source_data
    where is_aggregate_entity = false

)

select *
from standardized