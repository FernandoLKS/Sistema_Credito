from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from Pipelines.tasks.simulacao_tasks import (
    extract_task,
    simulate_task,
    transform_task,
    load_task
)

default_args = {
    'owner': 'fernando',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'pipelineSimulacao',
    default_args=default_args,
    schedule=None,
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_task
    )

    simulate = PythonOperator(
        task_id='simulate',
        python_callable=simulate_task
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_task
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_task
    )

    extract >> simulate >> transform >> load