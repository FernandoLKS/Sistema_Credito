from Funcoes.DataBase.conexoes import (
    executar_comando,
    inserir_dataframe
)

import logging

logger = logging.getLogger("airflow.task")


# ============================================
# LOG DETALHADO DE DATAFRAME
# ============================================
def log_dataframe(nome, df):
    if df is None:
        logger.info(f"{nome} é None")
        return

    for col in df.columns:
        logger.info(f" - {col}")

    logger.info("\n=========================\n")


# ============================================
# SALVAR ESTADO ATUAL
# ============================================
def salvar_estado_atual(resultado):
    clientes = resultado["clientes_atualizados"]
    operacoes = resultado["operacoes_atualizadas"]

    logger.info("=== Salvando estado atual ===")

    # 🔥 Log antes de salvar
    log_dataframe("clientes_atual", clientes)
    log_dataframe("operacoes_atual", operacoes)

    # Limpa tabelas
    executar_comando("TRUNCATE TABLE operacoes, clientes")

    # Insere dados
    inserir_dataframe("clientes", clientes)
    logger.info("=== CLIENTES INSERIDOS ===")
    inserir_dataframe("operacoes", operacoes)
    logger.info("=== OPERAÇÕES INSERIDAS ===")

    logger.info("Estado atual salvo com sucesso")


# ============================================
# SALVAR HISTÓRICO
# ============================================
def salvar_historico(resultado):
    logger.info("=== Salvando histórico ===")

    data_ref = resultado.get("data_ref")

    if data_ref is None:
        raise ValueError("data_ref não encontrado no resultado")

    clientes = resultado["clientes_atualizados"].copy()
    operacoes = resultado["operacoes_atualizadas"].copy()

    # 🔥 Log antes de alterar
    log_dataframe("clientes_historico_antes", clientes)
    log_dataframe("operacoes_historico_antes", operacoes)

    # Adiciona data de referência
    clientes["data_ref"] = data_ref
    operacoes["data_ref"] = data_ref

    # 🔥 Log depois de adicionar coluna
    log_dataframe("clientes_historico_depois", clientes)
    log_dataframe("operacoes_historico_depois", operacoes)

    inserir_dataframe("clientes_historico", clientes)
    inserir_dataframe("operacoes_historico", operacoes)

    logger.info("Histórico salvo com sucesso")


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def salvar_simulacao(resultado):
    logger.info("=== INICIANDO SALVAMENTO DA SIMULAÇÃO ===")

    salvar_estado_atual(resultado)
    salvar_historico(resultado)

    logger.info("=== SIMULAÇÃO SALVA COM SUCESSO ===")