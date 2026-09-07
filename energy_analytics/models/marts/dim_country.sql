with countries as (

    select distinct
        country_code,
        country_name

    from {{ ref('stg_electricity_demand') }}

    where country_code is not null
        and country_name is not null

)

select
    country_code,
    country_name

from countries