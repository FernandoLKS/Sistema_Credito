from datetime import datetime
import requests
import pandas as pd
import os
import json
from Funcoes.DataBase.conexoes import executar_sql
from Funcoes.DataBase.queries import Pegar_data_mais_recente
import logging

logger = logging.getLogger("airflow.task")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
caminho_json_relatorios = os.path.join(BASE_DIR, "relatorios.json")

def extrair(data_inicial=None, data_final=None):
    logger.info("Iniciando extração de dados do BCB...")

    def puxar_relatorio(codigo, data_inicial, data_final):
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
            f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # lança erro se status != 200
            data = response.json()
        except Exception as e:
            logger.warning(f"Erro ao puxar série {codigo}: {e}")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        if df.empty or "data" not in df.columns:
            logger.warning(f"Série {codigo} vazia")
            return pd.DataFrame()

        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        return df

    # Pegando a última data disponível no banco
    ultima_data = executar_sql(Pegar_data_mais_recente)[0][0]
    logger.info(f"Última data no banco: {ultima_data}")

    print(ultima_data)

    if ultima_data is None:
        logger.info("Banco vazio. Usando data inicial padrão.")
        ultima_data = pd.Timestamp("2011-03-01")

    proximo_mes = (ultima_data + pd.DateOffset(months=1)).replace(day=1)

    data_inicial = proximo_mes.strftime("%d/%m/%Y")
    data_final = proximo_mes.strftime("%d/%m/%Y")
    logger.info(f"Extraindo dados de {data_inicial} até {data_final}")

    with open(caminho_json_relatorios, "r", encoding="utf-8") as f:
        relatorios = json.load(f)

    df_final = None
    for nome, info in relatorios.items():
        logger.info(f"Extraindo série {nome} ({info['codigo']})")
        df = puxar_relatorio(info["codigo"], data_inicial, data_final)
        if df.empty:
            continue
        df = df.rename(columns={"valor": nome})
        if df_final is None:
            df_final = df
        else:
            df_final = df_final.merge(df, on="data", how="outer")

    if df_final is None or df_final.empty:
        logger.warning("Nenhum dado extraído. Task finalizada.")
        return None  # Airflow finaliza a task normalmente

    # df_final = df_final[df_final['inadimplencia_total'].notna()]
    logger.info(f"Extração concluída. Total de linhas: {len(df_final)}")
    logger.info(f"Exemplo de dados:\n{df_final.head()}")
    
    path = os.path.join(TEMP_DIR, "bcb_extract.parquet")
    df.to_parquet(path)
    return path