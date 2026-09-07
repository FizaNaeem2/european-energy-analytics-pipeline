select
    country_code,
    month,
    count(*) as row_count

from {{ ref('fct_carbon_intensity_forecast') }}

group by
    country_code,
    month

having count(*) > 1