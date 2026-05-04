import pandas as pd
import numpy as np

from Pipelines.src.transacoes.criacao_clientes import gerar_clientes_pf, gerar_clientes_pj
from Pipelines.src.transacoes.criacao_operacoes import (
    gerar_operacoes_mes,
    atualizar_inadimplencia,
    amortizar_operacoes,
    calcular_inadimplencia
)


def atualizar_operacoes(operacoes, taxa_pf, taxa_pj):
    if operacoes.empty:
        return operacoes

    operacoes = amortizar_operacoes(operacoes)
    operacoes = atualizar_inadimplencia(operacoes, taxa_pf, taxa_pj)
    return operacoes


def atualizar_clientes_inatividade(clientes, operacoes):
    ativos = set(operacoes["cliente_id"]) if not operacoes.empty else set()

    clientes = clientes.copy()
    clientes["inativo_meses"] = np.where(
        clientes["cliente_id"].isin(ativos),
        0,
        clientes["inativo_meses"] + 1
    )

    return clientes


def remover_clientes(clientes, prob):
    clientes = clientes.copy()

    candidatos = clientes[(clientes["inativo_meses"] >= 3) & (~clientes["removido"])]

    if not candidatos.empty:
        mask = np.random.rand(len(candidatos)) < prob
        clientes.loc[candidatos.index[mask], "removido"] = True

    return clientes


def gerar_novos_clientes(clientes, qtd_pf, qtd_pj):
    pf = gerar_clientes_pf(qtd_pf)
    pj = gerar_clientes_pj(qtd_pj)

    pf["tipo"] = "PF"
    pj["tipo"] = "PJ"

    pf["cliente_id"] = [f"PF_{i}" for i in range(len(pf))]
    pj["cliente_id"] = [f"PJ_{i}" for i in range(len(pj))]

    pf["inativo_meses"] = 0
    pj["inativo_meses"] = 0

    pf["removido"] = False
    pj["removido"] = False

    return pd.concat([clientes, pf, pj], ignore_index=True), pf, pj


def gerar_operacoes(clientes, concessoes_pf, concessoes_pj):
    ativos = clientes[~clientes["removido"]]

    return gerar_operacoes_mes(
        ativos,
        concessoes_pf,
        concessoes_pj
    )


def gerar_transacoes(
    data_ref,
    clientes,
    operacoes,
    concessoes_pf,
    concessoes_pj,
    taxa_pf_bcb,
    taxa_pj_bcb,
    novos_pf_qtd=200,
    novos_pj_qtd=50,
    prob_remocao=0.1
):

    clientes = clientes.copy()
    operacoes = operacoes.copy()

    operacoes = atualizar_operacoes(operacoes, taxa_pf_bcb, taxa_pj_bcb)

    clientes = atualizar_clientes_inatividade(clientes, operacoes)
    clientes = remover_clientes(clientes, prob_remocao)

    clientes, novos_pf, novos_pj = gerar_novos_clientes(
        clientes, novos_pf_qtd, novos_pj_qtd
    )

    novas_ops = gerar_operacoes(clientes, concessoes_pf, concessoes_pj)

    operacoes = pd.concat([operacoes, novas_ops], ignore_index=True)

    print(f"\n=== {data_ref} ===")
    print(f"Clientes ativos: {len(clientes[~clientes['removido']])}")
    print(f"Operações: {len(operacoes)}")
    print(f"Inadimplência: {calcular_inadimplencia(operacoes):.2%}")

    return {
        "data_ref": data_ref,
        "clientes": clientes,
        "operacoes": operacoes,
        "clientes_atualizados": pd.concat([novos_pf, novos_pj]),    
        "operacoes_atualizadas": novas_ops
    }