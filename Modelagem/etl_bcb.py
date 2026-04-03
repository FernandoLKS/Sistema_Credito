import pandas as pd
from datetime import datetime
from utils import get_bcb_series
import json

with open("Dados/relatorios.json", "r", encoding="utf-8") as f:
    relatorios = json.load(f)
df_final = None

data_inicial='01/01/2020'
data_final=datetime.today().strftime('%d/%m/%Y')

for nome, info in relatorios.items():
    
    print(f"Baixando: {nome}")    
    df = get_bcb_series(info["codigo"], data_inicial, data_final)    
    if df.empty:
        continue
    df = df.rename(columns={"valor": nome})
    if df_final is None:
        df_final = df
    else:
        df_final = df_final.merge(df, on="data", how="outer")

df_final = df_final[df_final['inadimplencia_total'].notnull()]

df_final = df_final.sort_values("data")
print(df_final)