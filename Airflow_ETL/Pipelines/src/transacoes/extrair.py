from Funcoes.DataBase.conexoes import consultar_dataframe, carregar_sql

def extrair_dados():
    data_ref = consultar_dataframe(
        carregar_sql("Data_mais_recente.sql")
    ).loc[0, 'ultima_data']

    informacoes_bcb = consultar_dataframe(
        carregar_sql("Informacoes_bcb.sql"),
        params=(data_ref,)
    )

    clientes = consultar_dataframe(
        carregar_sql("Clientes_ativos.sql")
    )

    operacoes = consultar_dataframe(
        carregar_sql("Operacoes_ativas.sql")
    )

    return data_ref, informacoes_bcb, clientes, operacoes