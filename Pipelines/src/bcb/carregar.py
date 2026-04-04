from Funcoes.DataBase.conexoes import get_connection
from psycopg2.extras import execute_batch
from Pipelines.src.bcb.transformar import transformar
from Pipelines.src.bcb.extrair import extrair

def carregar(df):
    conn = get_connection()
    cursor = conn.cursor()

    colunas = list(df.columns)

    colunas_sql = ", ".join(colunas)
    placeholders = ", ".join(["%s"] * len(colunas))

    update_sql = ", ".join([
        f"{col} = EXCLUDED.{col}"
        for col in colunas if col != "data"
    ])

    query = f"""
        INSERT INTO bcb_macro ({colunas_sql})
        VALUES ({placeholders})
        ON CONFLICT (data) DO UPDATE
        SET {update_sql}
    """

    dados = [tuple(row) for row in df.to_numpy()]

    execute_batch(cursor, query, dados)

    conn.commit()
    cursor.close()
    conn.close()

    print("Dados inseridos com sucesso!")

