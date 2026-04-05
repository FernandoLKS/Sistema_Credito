from Funcoes.DataBase.conexoes import executar_sql
from Funcoes.DataBase.queries import Inserir_Registro_bcb_macro

def carregar(df):
    if df is None or df.empty:
        print("DataFrame vazio. Nenhum dado será carregado.")
        return

    print("Iniciando carregamento no banco...")

    colunas = list(df.columns)
    colunas_sql = ", ".join(colunas)
    placeholders = ", ".join(["%s"] * len(colunas))
    update_sql = ", ".join([f"{col} = EXCLUDED.{col}" for col in colunas if col != "data"])

    # Formata a query do arquivo queries.py
    query = Inserir_Registro_bcb_macro.format(
        colunas=colunas_sql,
        placeholders=placeholders,
        update_sql=update_sql
    )

    # Converte DataFrame em lista de tuplas
    dados = [tuple(x) for x in df.to_numpy()]

    print(dados)
    # Executa SQL usando sua função
    executar_sql(query, params=dados, many=True, fetch=False)

    print("Dados inseridos com sucesso!")