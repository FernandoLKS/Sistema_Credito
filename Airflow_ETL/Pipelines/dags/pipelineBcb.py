from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import logging

from Pipelines.src.bcb.extrair import extrair
from Pipelines.src.bcb.transformar import transformar
from Pipelines.src.bcb.carregar import carregar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "../temp")

def extract_task(**context):
    df = extrair()

    path = os.path.join(TEMP_DIR, "bcb_extract.parquet")
    df.to_parquet(path)
    return path

def transform_task(**context):
    import pandas as pd

    ti = context['ti']
    path = ti.xcom_pull(task_ids='extract')

    df = pd.read_parquet(path)
    df = transformar(df)

    path = os.path.join(TEMP_DIR, "bcb_extract.parquet")
    df.to_parquet(path)

    return path


def load_task(**context):
    import pandas as pd

    ti = context['ti']
    path = ti.xcom_pull(task_ids='transform')

    df = pd.read_parquet(path)
    logging.info(df.head())

    carregar(df)


default_args = {
    'owner': 'fernando',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'pipelineBcb',
    default_args=default_args,
    schedule=None,
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_task
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_task
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_task
    )

    extract >> transform >> load