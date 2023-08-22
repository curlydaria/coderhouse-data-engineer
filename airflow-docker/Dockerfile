FROM python:3.8

RUN pip install apache-airflow==2.3.3
RUN airflow db init

COPY ./docker-compose.yaml .
COPY ./dags /opt/airflow/dags
COPY ./logs /opt/airflow/logs
COPY ./plugins /opt/airflow/plugins

WORKDIR /opt/airflow/

EXPOSE 8080

# execute docker-compose up



