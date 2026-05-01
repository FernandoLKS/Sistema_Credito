import pandas as pd
import numpy as np
from criacao_clientes import gerar_clientes_pf, gerar_clientes_pj
from criacao_operacoes import gerar_operacoes_mes, atualizar_inadimplencia, amortizar_operacoes, calcular_inadimplencia

def gerar_transacoes(data_ref, clientes, operacoes, concessoes_pf, concessoes_pj, taxa_pf_bcb, taxa_pj_bcb, novos_pf_qtd=200, novos_pj_qtd=50, prob_remocao=0.1):

    print(f"\n=== Rodando mês {data_ref} ===")

    if not operacoes.empty:
        operacoes = amortizar_operacoes(operacoes)

    ativos_ids = set(operacoes["cliente_id"].unique())

    clientes["tem_operacao"] = clientes["cliente_id"].isin(ativos_ids)

    clientes.loc[~clientes["tem_operacao"], "inativo_meses"] += 1
    clientes.loc[clientes["tem_operacao"], "inativo_meses"] = 0

    # candidatos a remoção
    candidatos = clientes[
        (clientes["inativo_meses"] >= 3) &
        (~clientes["removido"])
    ]

    if len(candidatos) > 0:
        mask = np.random.rand(len(candidatos)) < prob_remocao
        clientes.loc[candidatos.index[mask], "removido"] = True

    novos_pf = gerar_clientes_pf(novos_pf_qtd)
    novos_pf["tipo"] = "PF"

    novos_pj = gerar_clientes_pj(novos_pj_qtd)
    novos_pj["tipo"] = "PJ"

    # IDs (IMPORTANTE evitar colisão)
    max_pf = clientes[clientes["tipo"] == "PF"].shape[0]
    max_pj = clientes[clientes["tipo"] == "PJ"].shape[0]

    novos_pf["cliente_id"] = [f"PF_{max_pf + i}" for i in range(len(novos_pf))]
    novos_pj["cliente_id"] = [f"PJ_{max_pj + i}" for i in range(len(novos_pj))]

    novos_pf["inativo_meses"] = 0
    novos_pf["removido"] = False

    novos_pj["inativo_meses"] = 0
    novos_pj["removido"] = False

    clientes = pd.concat([clientes, novos_pf, novos_pj], ignore_index=True)

    clientes_ativos = clientes[~clientes["removido"]]

    novas_op = gerar_operacoes_mes(
        clientes_ativos,
        concessoes_pf,
        concessoes_pj,
        seed=None
    )

    operacoes = pd.concat([operacoes, novas_op], ignore_index=True)

    operacoes = atualizar_inadimplencia(
        operacoes,
        taxa_pf=taxa_pf_bcb,
        taxa_pj=taxa_pj_bcb
    )

    taxa_total = calcular_inadimplencia(operacoes)

    taxa_pf = calcular_inadimplencia(
        operacoes[operacoes["tipo"] == "PF"]
    )

    taxa_pj = calcular_inadimplencia(
        operacoes[operacoes["tipo"] == "PJ"]
    )

    print(f"Clientes ativos: {(~clientes['removido']).sum()}")
    print(f"Operações: {len(operacoes)}")
    print(f"Inadimplência total: {taxa_total:.2%}")
    print(f"PF: {taxa_pf:.2%} | PJ: {taxa_pj:.2%}")

    return {"clientes_atualizados": clientes, "operacoes_atualizadas": operacoes, "novos_clientes": pd.concat([novos_pf, novos_pj]), "novas_operacoes": novas_op}

# clientes_pf = gerar_clientes_pf(3000, seed=42)
# clientes_pf["tipo"] = "PF"
# clientes_pf["cliente_id"] = [f"PF_{i}" for i in range(len(clientes_pf))]

# clientes_pj = gerar_clientes_pj(500, seed=42)
# clientes_pj["tipo"] = "PJ"
# clientes_pj["cliente_id"] = [f"PJ_{i}" for i in range(len(clientes_pj))]

# clientes = pd.concat([clientes_pf, clientes_pj], ignore_index=True)

# contador_pf = len(clientes_pf)
# contador_pj = len(clientes_pj)

# operacoes = pd.DataFrame()

# taxa_pf_bcb = 0.05
# taxa_pj_bcb = 0.03

# for mes in range(1, 10):

#     print(f"\n=== Mês {mes} ===")

#     if not operacoes.empty:
#         operacoes = amortizar_operacoes(operacoes)

#     novos_pf = gerar_clientes_pf(200)
#     novos_pf["tipo"] = "PF"
#     novos_pf["cliente_id"] = [f"PF_{contador_pf + i}" for i in range(len(novos_pf))]
#     contador_pf += len(novos_pf)

#     novos_pj = gerar_clientes_pj(50)
#     novos_pj["tipo"] = "PJ"
#     novos_pj["cliente_id"] = [f"PJ_{contador_pj + i}" for i in range(len(novos_pj))]
#     contador_pj += len(novos_pj)

#     clientes = pd.concat([clientes, novos_pf, novos_pj], ignore_index=True)

#     concessoes_pf = 10_000_000 + mes * 100_000
#     concessoes_pj = 20_000_000 + mes * 200_000

#     novas_op = gerar_operacoes_mes(
#         clientes,
#         concessoes_pf,
#         concessoes_pj,
#         seed=mes
#     )

#     operacoes = pd.concat([operacoes, novas_op], ignore_index=True)

#     operacoes = atualizar_inadimplencia(
#         operacoes,
#         taxa_pf=taxa_pf_bcb,
#         taxa_pj=taxa_pj_bcb
#     )

#     total_clientes = len(clientes)
#     total_operacoes = len(operacoes)

#     taxa_total = calcular_inadimplencia(operacoes)

#     taxa_pf = calcular_inadimplencia(
#         operacoes[operacoes["tipo"] == "PF"]
#     )

#     taxa_pj = calcular_inadimplencia(
#         operacoes[operacoes["tipo"] == "PJ"]
#     )

#     print(f"Clientes totais: {total_clientes}")
#     print(f"Operações ativas: {total_operacoes}")

#     print(f"Inadimplência total: {taxa_total:.2%}")
#     print(f"Inadimplência PF: {taxa_pf:.2%} (alvo: {taxa_pf_bcb:.2%})")
#     print(f"Inadimplência PJ: {taxa_pj:.2%} (alvo: {taxa_pj_bcb:.2%})")

#     print("\nSaldo por status:")
#     print(operacoes.groupby("status")["saldo_devedor"].sum())

# operacoes.to_excel("carteira_simulada.xlsx", index=False)
# clientes.to_excel("clientes_simulados.xlsx", index=False)