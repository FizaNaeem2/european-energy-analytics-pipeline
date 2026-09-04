with source_data as (

    select *
    from {{ source('raw', 'raw_electricity_demand') }}

),

standardized as (

    select
        trim(entity) as country_name,
        upper(trim(entity_code)) as country_code,
        cast(date as date) as month,
        cast(demand_twh as double) as demand_twh

    from source_data

    where is_aggregate_entity = false

)

select *
from standardized