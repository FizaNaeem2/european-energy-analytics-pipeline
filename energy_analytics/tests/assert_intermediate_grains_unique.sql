with generation_duplicates as (

    select
        'int_generation_monthly' as model_name,
        country_code,
        month,
        count(*) as row_count

    from {{ ref('int_generation_monthly') }}

    group by
        country_code,
        month

    having count(*) > 1

),

emissions_duplicates as (

    select
        'int_emissions_monthly' as model_name,
        country_code,
        month,
        count(*) as row_count

    from {{ ref('int_emissions_monthly') }}

    group by
        country_code,
        month

    having count(*) > 1

)

select *
from generation_duplicates

union all

select *
from emissions_duplicates