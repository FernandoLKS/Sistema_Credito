from Funcoes.DataBase.conexoes import inserir_dataframe

def carregar(df):
    if df is None or df.empty:
        print("DataFrame vazio. Nenhum dado será carregado.")
        return

    print("Iniciando carregamento no banco...")

    inserir_dataframe("bcb_macro", df)

    print("Dados inseridos com sucesso!")