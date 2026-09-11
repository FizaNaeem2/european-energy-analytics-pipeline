FROM apache/airflow:3.3.1

COPY requirements-airflow.txt /requirements-airflow.txt

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    -r /requirements-airflow.txt

USER root

RUN mkdir -p \
    /opt/airflow/project/data/raw \
    /opt/airflow/project/data/warehouse \
    /opt/airflow/project/data/power_bi \
    && chown -R airflow:root /opt/airflow/project

USER airflow

COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root src /opt/airflow/project/src
COPY --chown=airflow:root energy_analytics /opt/airflow/project/energy_analytics
COPY --chown=airflow:root config /opt/airflow/project/config
COPY --chown=airflow:root power_bi /opt/airflow/project/power_bi

WORKDIR /opt/airflow/project