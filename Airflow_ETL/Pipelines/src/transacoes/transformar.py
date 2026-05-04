import pandas as pd
import numpy as np

def transformar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # remover duplicadas de coluna
    df = df.loc[:, ~df.columns.duplicated()]

    # padronizar nomes
    rename_map = {
        "numero_funcionarios": "num_funcionarios"
    }
    df = df.rename(columns=rename_map)

    # garantir colunas esperadas
    colunas_num = [
        "idade", "score", "renda", "comprometimento_renda",
        "tempo_empresa", "patrimonio", "tempo_relacionamento",
        "faturamento_mensal", "faturamento_anual",
        "margem_lucro", "alavancagem",
        "num_funcionarios", "historico_atraso"
    ]

    for col in colunas_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # inteiros
    col_int = ["idade", "tempo_empresa", "tempo_relacionamento",
               "num_funcionarios", "historico_atraso"]

    for col in col_int:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    # booleanos
    if "removido" in df.columns:
        df["removido"] = df["removido"].astype(bool)

    # timestamps
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df

def transformar_operacoes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.loc[:, ~df.columns.duplicated()]

    # ids
    df["id"] = df["id"].astype(str)

    # numéricos
    col_num = [
        "pd", "valor", "juros", "saldo_devedor",
        "parcela_valor"
    ]

    for col in col_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # inteiros críticos
    col_int = [
        "prazo", "parcelas_total", "parcelas_pagas",
        "meses_em_atraso"
    ]

    for col in col_int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # datas
    if "data_contratacao" in df.columns:
        df["data_contratacao"] = pd.to_datetime(df["data_contratacao"], errors="coerce")

    return df