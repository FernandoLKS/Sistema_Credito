import psycopg2
import os
import pandas as pd
from psycopg2.extras import execute_values

DB_CONFIG = {
    "dbname": "credito_data",
    "user": "postgres",
    "password": "postgres",
    "host": "host.docker.internal",
    "port": "5433"
}


def obter_conexao():
    return psycopg2.connect(**DB_CONFIG)


def carregar_sql(nome_arquivo):
    caminho = os.path.join(
        os.path.dirname(__file__),
        "..",
        "Queries",
        nome_arquivo
    )

    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def consultar_dataframe(query, params=None):
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)

            rows = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]

            return pd.DataFrame(rows, columns=colunas)

    finally:
        conn.close()


def executar_comando(query, params=None):
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


def inserir_dataframe(tabela, df):
    if df is None or df.empty:
        return

    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            colunas = ", ".join(df.columns)

            query = f"""
                INSERT INTO {tabela} ({colunas})
                VALUES %s
            """

            execute_values(cursor, query, df.values.tolist())

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()