with expected_forecasts as (

    select
        country_code,
        month,

        lag(carbon_intensity_gco2_per_kwh, 1)
            over (
                partition by country_code
                order by month
            )
            as expected_prediction

    from {{ ref('fct_country_monthly_energy') }}

    where carbon_intensity_gco2_per_kwh is not null

),

forecast_violations as (

    select
        forecast.*

    from {{ ref('fct_carbon_intensity_forecast') }} as forecast

    left join expected_forecasts as expected
        on forecast.country_code = expected.country_code
        and forecast.month = expected.month

    where expected.expected_prediction is null

        or abs(
            forecast.predicted_carbon_intensity_gco2_per_kwh
            - expected.expected_prediction
        ) > 0.000001

        or abs(
            forecast.absolute_error_gco2_per_kwh
            - abs(forecast.forecast_error_gco2_per_kwh)
        ) > 0.000001

        or abs(
            forecast.squared_error
            - power(forecast.forecast_error_gco2_per_kwh, 2)
        ) > 0.000001

        or forecast.absolute_error_gco2_per_kwh < 0

        or forecast.squared_error < 0

)

select *
from forecast_violations