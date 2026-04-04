from datetime import datetime
import requests
import pandas as pd
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_json_relatorios = os.path.join(BASE_DIR, "relatorios.json")

def extrair(data_inicial='01/03/2011', data_final='01/04/2011'):
    def puxar_relatorio(codigo, data_inicial, data_final):
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
            f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
        )
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erro na série {codigo}: {response.text}")
            return pd.DataFrame()

        data = response.json()
        df = pd.DataFrame(data)

        if df.empty or "data" not in df.columns:
            print(f"Série {codigo} vazia")
            return pd.DataFrame()

        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        return df

    with open(caminho_json_relatorios, "r", encoding="utf-8") as f:
        relatorios = json.load(f)
    df_final = None

    for nome, info in relatorios.items():
        print(nome)
        df = puxar_relatorio(info["codigo"], data_inicial, data_final)    
        if df.empty:
            continue
        df = df.rename(columns={"valor": nome})
        if df_final is None:
            df_final = df
        else:
            df_final = df_final.merge(df, on="data", how="outer")

    df_final = df_final[df_final['inadimplencia_total'].notna()]
    df_final = df_final.sort_values("data")

    return df_final

