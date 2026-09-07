with months as (

    select distinct
        month as month_start

    from {{ ref('fct_country_monthly_energy') }}

    where month is not null

)

select
    cast(strftime(month_start, '%Y%m') as integer)
        as month_key,

    month_start,

    cast(extract(year from month_start) as integer)
        as calendar_year,

    cast(extract(month from month_start) as integer)
        as calendar_month_number,

    'Q'
    || cast(extract(quarter from month_start) as integer)
        as calendar_quarter,

    strftime(month_start, '%B')
        as month_name,

    strftime(month_start, '%Y-%m')
        as year_month

from months