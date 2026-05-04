import os
import pandas as pd

from Pipelines.src.transacoes.extrair import extrair_dados
from Pipelines.src.transacoes.simular import rodar_simulacao
from Pipelines.src.transacoes.salvar import salvar_simulacao
from Pipelines.src.transacoes.transformar import transformar_clientes, transformar_operacoes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "../temp")

def extract_task(**context):
    data_ref, bcb, clientes, operacoes = extrair_dados()

    payload = {
        "data_ref": data_ref,
        "bcb": bcb,
        "clientes": clientes,
        "operacoes": operacoes
    }

    path = os.path.join(TEMP_DIR, "sim_extract.pkl")
    pd.to_pickle(payload, path)

    return path

def simulate_task(**context):
    ti = context["ti"]
    path = ti.xcom_pull(task_ids="extract")

    payload = pd.read_pickle(path)

    clientes, operacoes, bcb, data_ref = (
        payload["clientes"],
        payload["operacoes"],
        payload["bcb"],
        payload["data_ref"]
    )

    resultado = rodar_simulacao(
        data_ref=data_ref,
        clientes=clientes,
        operacoes=operacoes,
        informacoes_bcb=bcb
    )

    path_out = os.path.join(TEMP_DIR, "simulate.pkl")
    pd.to_pickle(resultado, path_out)

    return path_out

def transform_task(**context):
    ti = context["ti"]
    path = ti.xcom_pull(task_ids="simulate")

    payload = pd.read_pickle(path)

    resultado = {
        "data_ref": payload["data_ref"],
        "clientes": transformar_clientes(payload["clientes"]),
        "operacoes": transformar_operacoes(payload["operacoes"]),
        "clientes_atualizados": transformar_clientes(payload["clientes_atualizados"]),    
        "operacoes_atualizadas": transformar_clientes(payload["operacoes_atualizadas"])
    }

    path_out = os.path.join(TEMP_DIR, "transform.pkl")
    pd.to_pickle(resultado, path_out)

    return path_out

def load_task(**context):
    ti = context['ti']
    path = ti.xcom_pull(task_ids='transform')

    resultado = pd.read_pickle(path)
    salvar_simulacao(resultado)