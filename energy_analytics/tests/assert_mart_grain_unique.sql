select
    country_code,
    month,
    count(*) as row_count

from {{ ref('fct_country_monthly_energy') }}

group by
    country_code,
    month

having count(*) > 1