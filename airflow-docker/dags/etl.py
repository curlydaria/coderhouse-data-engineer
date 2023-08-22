from datetime import timedelta,datetime
from airflow import DAG
# Operadores
from airflow.operators.python_operator import PythonOperator
#from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator

from functions import *




# arguments of the DAG
default_args = {
    'owner': 'Sol',
    'start_date': datetime(2023,8,22),
    'retries':3,
    'retry_delay': timedelta(minutes=3)
}

products_dag = DAG(
    dag_id='ETL_products',
    default_args=default_args,
    description='Agrega data de productos de forma diaria',
    schedule_interval="@daily",
    catchup=False
)

# Tasks
##1. Extract data from api
task_1 = PythonOperator(
    task_id='extraer_data',
    python_callable=get_data,
    dag=products_dag,
)

#2. Transform data
task_2 = PythonOperator(
    task_id='transformar_data',
    python_callable=process_data,
    dag=products_dag,
)

#3. Test Redshift connection
task_3 = PythonOperator(
    task_id='comprobar_conexion',
    python_callable=redshift_conn,
    dag=products_dag,
)

#4. Insert data
task_4 = PythonOperator(
    task_id='insertar_data',
    python_callable=insert_data,
    dag=products_dag,
)


# Tasks order
task_1 >> task_2 >> task_3 >> task_4



