with monthly_carbon_intensity as (

    select
        country_code,
        month,
        carbon_intensity_gco2_per_kwh

    from {{ ref('fct_country_monthly_energy') }}

    where carbon_intensity_gco2_per_kwh is not null

),

persistence_forecast as (

    select
        country_code,
        month,

        carbon_intensity_gco2_per_kwh
            as actual_carbon_intensity_gco2_per_kwh,

        lag(carbon_intensity_gco2_per_kwh, 1)
            over (
                partition by country_code
                order by month
            )
            as predicted_carbon_intensity_gco2_per_kwh

    from monthly_carbon_intensity

),

forecast_errors as (

    select
        country_code,
        month,

        actual_carbon_intensity_gco2_per_kwh,
        predicted_carbon_intensity_gco2_per_kwh,

        actual_carbon_intensity_gco2_per_kwh
        - predicted_carbon_intensity_gco2_per_kwh
            as forecast_error_gco2_per_kwh,

        abs(
            actual_carbon_intensity_gco2_per_kwh
            - predicted_carbon_intensity_gco2_per_kwh
        )
            as absolute_error_gco2_per_kwh,

        power(
            actual_carbon_intensity_gco2_per_kwh
            - predicted_carbon_intensity_gco2_per_kwh,
            2
        )
            as squared_error,

        case
            when month < date '2023-01-01'
                then 'Training history'
            when month < date '2025-01-01'
                then 'Validation'
            else 'Final test'
        end
            as evaluation_split,

        'Previous-month persistence'
            as forecast_method

    from persistence_forecast

)

select *
from forecast_errors

where predicted_carbon_intensity_gco2_per_kwh is not null