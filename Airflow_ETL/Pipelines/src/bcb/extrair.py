from datetime import datetime
import requests
import pandas as pd
import os
import json
import logging

from Funcoes.DataBase.conexoes import consultar_dataframe, carregar_sql

logger = logging.getLogger("airflow.task")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
caminho_json_relatorios = os.path.join(BASE_DIR, "relatorios.json")


def puxar_relatorio(codigo, data_inicial, data_final):
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.warning(f"Erro ao puxar série {codigo}: {e}")
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if "data" not in df.columns:
        return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    if codigo == "432":
        df = df[df["data"].dt.day == 1]

    return df


def extrair():
    logger.info("=== Iniciando extração de dados do BCB ===")

    resultado = consultar_dataframe(
        carregar_sql("Data_mais_recente.sql")
    )

    if resultado.empty or resultado.loc[0, "ultima_data"] is None:
        logger.info("Banco vazio. Usando data inicial padrão.")
        ultima_data = pd.Timestamp("2011-03-01")
    else:
        ultima_data = pd.to_datetime(resultado.loc[0, "ultima_data"])

    logger.info(f"Última data no banco: {ultima_data}")

    proximo_mes = (ultima_data + pd.DateOffset(months=1)).replace(day=1)
    hoje = pd.Timestamp.today().replace(day=1)

    if proximo_mes > hoje:
        logger.info("Não há novos dados disponíveis.")
        return None

    data_inicial = proximo_mes.strftime("%d/%m/%Y")
    data_final = proximo_mes.strftime("%d/%m/%Y")

    logger.info(f"Buscando dados de {data_inicial} até {data_final}")

    with open(caminho_json_relatorios, "r", encoding="utf-8") as f:
        relatorios = json.load(f)

    df_final = None
    colunas_esperadas = list(relatorios.keys())

    for nome, info in relatorios.items():
        codigo = info["codigo"]
        logger.info(f"Extraindo série {nome} ({codigo})")

        df = puxar_relatorio(codigo, data_inicial, data_final)

        if df.empty:
            continue

        df = df.rename(columns={"valor": nome})

        if df_final is None:
            df_final = df
        else:
            df_final = df_final.merge(df, on="data", how="outer")

    if df_final is None:
        logger.info("Nenhum dado retornado das APIs.")
        return None

    faltantes = [col for col in colunas_esperadas if col not in df_final.columns]
    if faltantes:
        raise ValueError(f"Colunas faltantes no DF final: {faltantes}")

    df_final = df_final[df_final["data"] > ultima_data]

    if df_final.empty:
        logger.info("Nenhum dado novo após filtro.")
        return None

    df_final = df_final.sort_values("data")

    logger.info(f"Extração concluída: {len(df_final)} linhas")
    logger.info(f"Período: {df_final['data'].min()} → {df_final['data'].max()}")

    return df_final