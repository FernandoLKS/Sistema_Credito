import numpy as np
import pandas as pd
import random


# =========================
# 1. GERAÇÃO DE OPERAÇÕES
# =========================

def gerar_operacoes_mes(
    clientes,
    concessoes_pf,
    concessoes_pj,
    min_valor=1000,
    seed=None
):
    rng = np.random.default_rng(seed)
    novas_operacoes = []

    def gerar(tipo, novo_credito, mean, sigma, prazo_opts, juros_range):
        clientes_tipo = clientes[clientes["tipo"] == tipo]

        if novo_credito <= min_valor or clientes_tipo.empty:
            return []

        qtd = max(1, int(novo_credito / mean))

        # amostra clientes
        clientes_sample = clientes_tipo.sample(n=qtd, replace=True)

        # gera valores
        valores = rng.lognormal(mean=np.log(mean), sigma=sigma, size=qtd)
        valores *= novo_credito / valores.sum()

        ops = []

        for i, (_, cliente) in enumerate(clientes_sample.iterrows()):
            valor = valores[i]

            # vínculo com cliente
            if tipo == "PF":
                valor = min(valor, cliente["renda"] * rng.uniform(2, 6))
            else:
                valor = min(valor, cliente["faturamento_anual"] * rng.uniform(0.05, 0.2))

            prazo = random.choice(prazo_opts)

            # juros baseado em risco (score)
            juros_base = rng.uniform(*juros_range)
            juros = juros_base + cliente["pd"] * 0.05

            ops.append({
                "cliente_id": cliente["cliente_id"],
                "tipo": tipo,
                "pd": cliente["pd"],

                "valor": valor,
                "prazo": prazo,
                "juros": juros,

                "saldo_devedor": valor,
                "parcelas_total": prazo,
                "parcelas_pagas": 0,
                "parcela_valor": valor / prazo,

                "status": "ativa",
                "meses_em_atraso": 0
            })

        return ops

    novas_operacoes += gerar(
        "PF", concessoes_pf,
        mean=5_000, sigma=0.5,
        prazo_opts=[12, 24, 36],
        juros_range=(0.02, 0.05)
    )

    novas_operacoes += gerar(
        "PJ", concessoes_pj,
        mean=100_000, sigma=0.6,
        prazo_opts=[24, 36, 60],
        juros_range=(0.01, 0.04)
    )

    return pd.DataFrame(novas_operacoes)


# =========================
# 2. INADIMPLÊNCIA (RANK + CALIBRAÇÃO)
# =========================

def atualizar_inadimplencia(
    df,
    taxa_pf,
    taxa_pj,
    prob_migra_ativa_30=0.03,
    prob_migra_30_60=0.5,
    prob_migra_60_90=0.5,
    prob_regulariza=0.2
):
    df = df.copy()

    # -------------------------
    # 1. dinâmica base
    # -------------------------
    for i, row in df.iterrows():

        if row["status"] == "ativa":
            if np.random.rand() < prob_migra_ativa_30:
                df.at[i, "status"] = "over 30"

        elif row["status"] == "over 30":
            if np.random.rand() < prob_migra_30_60:
                df.at[i, "status"] = "over 60"
            elif np.random.rand() < prob_regulariza:
                df.at[i, "status"] = "ativa"

        elif row["status"] == "over 60":
            if np.random.rand() < prob_migra_60_90:
                df.at[i, "status"] = "over 90"
            elif np.random.rand() < prob_regulariza:
                df.at[i, "status"] = "ativa"

    # incrementa atraso
    df.loc[df["status"] != "ativa", "meses_em_atraso"] += 1

    # -------------------------
    # 2. calibração via ranking (PD)
    # -------------------------

    def ajustar(tipo, taxa_alvo):
        sub = df[df["tipo"] == tipo]

        saldo_total = sub["saldo_devedor"].sum()
        alvo = taxa_alvo * saldo_total

        atual = sub[sub["status"] == "over 90"]["saldo_devedor"].sum()

        # aumentar inadimplência
        if atual < alvo:
            candidatos = sub[sub["status"].isin(["over 60", "over 30", "ativa"])]
            candidatos = candidatos.sort_values("pd", ascending=False)

            acumulado = atual

            for idx, row in candidatos.iterrows():
                if acumulado >= alvo:
                    break
                df.at[idx, "status"] = "over 90"
                acumulado += row["saldo_devedor"]

        # reduzir inadimplência
        elif atual > alvo:
            candidatos = sub[sub["status"] == "over 90"]
            candidatos = candidatos.sort_values("pd", ascending=True)

            acumulado = atual

            for idx, row in candidatos.iterrows():
                if acumulado <= alvo:
                    break
                df.at[idx, "status"] = "ativa"
                acumulado -= row["saldo_devedor"]

    ajustar("PF", taxa_pf)
    ajustar("PJ", taxa_pj)

    return df


# =========================
# 3. AMORTIZAÇÃO
# =========================

def amortizar_operacoes(df):
    df = df.copy()

    mask = df["status"] == "ativa"

    df.loc[mask, "saldo_devedor"] -= df.loc[mask, "parcela_valor"]
    df.loc[mask, "parcelas_pagas"] += 1

    return df[df["parcelas_pagas"] < df["parcelas_total"]]


# =========================
# 4. MÉTRICA
# =========================

def calcular_inadimplencia(df):
    saldo_total = df["saldo_devedor"].sum()
    saldo_over90 = df.loc[df["status"] == "over 90", "saldo_devedor"].sum()

    return saldo_over90 / saldo_total if saldo_total > 0 else 0