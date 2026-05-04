import numpy as np
import pandas as pd


def gerar_operacoes_mes(clientes, concessoes_pf, concessoes_pj, min_valor=1000, seed=None):
    rng = np.random.default_rng(seed)

    def gerar_bloco(tipo, concessao, mean, sigma, prazo_opts, juros_range):
        base = clientes[clientes["tipo"] == tipo]

        if base.empty or concessao <= min_valor:
            return pd.DataFrame()

        qtd = max(1, int(concessao / mean))
        sample = base.sample(n=qtd, replace=True, random_state=rng).reset_index(drop=True)

        valores = rng.lognormal(np.log(mean), sigma, size=qtd)
        concessao = float(concessao)
        valores = valores * (concessao / valores.sum())

        limite = (
            sample["renda"] * rng.uniform(2, 6, size=qtd)
            if tipo == "PF"
            else sample["faturamento_anual"] * rng.uniform(0.05, 0.2, size=qtd)
        )

        valores = np.minimum(valores, limite)

        prazo = rng.choice(prazo_opts, size=qtd)

        df = pd.DataFrame({
            "cliente_id": sample["cliente_id"].values,
            "tipo": tipo,
            "pd": sample["pd"].values,
            "valor": valores,
            "prazo": prazo,
            "juros": rng.uniform(*juros_range, size=qtd) + sample["pd"] * 0.05,
            "saldo_devedor": valores,
            "parcelas_total": prazo,
            "parcelas_pagas": 0,
            "parcela_valor": valores / prazo,
            "status": "ativa",
            "meses_em_atraso": 0
        })

        return df

    pf = gerar_bloco("PF", concessoes_pf, 5000, 0.5, [12, 24, 36], (0.02, 0.05))
    pj = gerar_bloco("PJ", concessoes_pj, 100000, 0.6, [24, 36, 60], (0.01, 0.04))

    return pd.concat([pf, pj], ignore_index=True)


def atualizar_inadimplencia(df, taxa_pf, taxa_pj,
                             p_ativa_30=0.03,
                             p_30_60=0.5,
                             p_60_90=0.5,
                             p_regulariza=0.2):

    df = df.copy()
    r = np.random.rand(len(df))

    df.loc[(df["status"] == "ativa") & (r < p_ativa_30), "status"] = "over 30"
    df.loc[(df["status"] == "over 30") & (r < p_30_60), "status"] = "over 60"
    df.loc[(df["status"] == "over 30") & (r > p_30_60) & (r < p_30_60 + p_regulariza), "status"] = "ativa"
    df.loc[(df["status"] == "over 60") & (r < p_60_90), "status"] = "over 90"
    df.loc[(df["status"] == "over 60") & (r > p_60_90) & (r < p_60_90 + p_regulariza), "status"] = "ativa"

    df.loc[df["status"] != "ativa", "meses_em_atraso"] += 1

    def ajustar(tipo, alvo):
        sub = df[df["tipo"] == tipo]
        if sub.empty:
            return

        total = sub["saldo_devedor"].sum()
        objetivo = total * alvo

        atual = sub.loc[sub["status"] == "over 90", "saldo_devedor"].sum()

        if atual < objetivo:
            candidatos = sub[sub["status"] != "over 90"].sort_values("pd", ascending=False)
            acc = atual

            for idx in candidatos.index:
                if acc >= objetivo:
                    break
                df.at[idx, "status"] = "over 90"
                acc += df.at[idx, "saldo_devedor"]

        elif atual > objetivo:
            candidatos = sub[sub["status"] == "over 90"].sort_values("pd")
            acc = atual

            for idx in candidatos.index:
                if acc <= objetivo:
                    break
                df.at[idx, "status"] = "ativa"
                acc -= df.at[idx, "saldo_devedor"]

    ajustar("PF", taxa_pf)
    ajustar("PJ", taxa_pj)

    return df


def amortizar_operacoes(df):
    df = df.copy()

    mask = df["status"] == "ativa"
    df.loc[mask, "saldo_devedor"] -= df.loc[mask, "parcela_valor"]
    df.loc[mask, "parcelas_pagas"] += 1

    return df[df["parcelas_pagas"] < df["parcelas_total"]].reset_index(drop=True)


def calcular_inadimplencia(df):
    total = df["saldo_devedor"].sum()
    if total == 0:
        return 0

    return df.loc[df["status"] == "over 90", "saldo_devedor"].sum() / total