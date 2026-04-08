import os
import logging
import pandas as pd

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
    ti = context['ti']
    path = ti.xcom_pull(task_ids='extract')

    df = pd.read_parquet(path)
    df = transformar(df)

    path = os.path.join(TEMP_DIR, "bcb_transform.parquet")
    df.to_parquet(path)

    return path


def load_task(**context):
    ti = context['ti']
    path = ti.xcom_pull(task_ids='transform')

    df = pd.read_parquet(path)
    logging.info(df.head())

    carregar(df)