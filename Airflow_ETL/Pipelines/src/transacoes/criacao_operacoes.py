import numpy as np
import pandas as pd
import random

# -----------------------------
# Geração de operações
# -----------------------------
def gerar_operacoes_mes(concessoes_pf, concessoes_pj, min_valor=1000):
    novas_operacoes = []
    
    def gerar(tipo, novo_credito, mean, sigma, prazo_opts, juros_range):
        if novo_credito <= min_valor:
            return []
        
        qtd_estimada = int(novo_credito / mean)
        if qtd_estimada < 1:
            qtd_estimada = 1
        
        valores = np.random.lognormal(mean=np.log(mean), sigma=sigma, size=qtd_estimada)
        escala = novo_credito / valores.sum()
        valores = valores * escala
        
        ops = []
        for valor in valores:
            prazo = random.choice(prazo_opts)
            juros = np.random.uniform(*juros_range)
            parcela_valor = valor / prazo
            ops.append({
                "tipo": tipo,
                "valor": valor,
                "prazo": prazo,
                "juros": juros,
                "saldo_devedor": valor,
                "parcelas_total": prazo,
                "parcelas_pagas": 0,
                "parcela_valor": parcela_valor,
                "status": "ativa",
                "meses_em_atraso": 0
            })
        return ops
    
    novas_operacoes += gerar("PF", concessoes_pf, 5_000, 0.5, [12, 24, 36], (0.02, 0.05))
    novas_operacoes += gerar("PJ", concessoes_pj, 100_000, 0.6, [24, 36, 60], (0.01, 0.04))
    
    return pd.DataFrame(novas_operacoes)


# -----------------------------
# Atualização da inadimplência
# -----------------------------
def atualizar_inadimplencia(df, taxa_pf, taxa_pj,
                            prob_migra_ativa_30=0.05,
                            prob_migra_30_60=0.5,
                            prob_migra_60_90=0.5,
                            prob_regulariza=0.2,
                            limite_over90=6):
    df = df.copy()
    
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
    
    # incrementa meses em atraso
    df.loc[df["status"] != "ativa", "meses_em_atraso"] += 1
    
    # remove operações que ficaram muito tempo em over 90
    df = df[~((df["status"]=="over 90") & (df["meses_em_atraso"] >= limite_over90))]
    
    # Calibração para bater saldo em over 90
    saldo_pf_total = df.loc[df["tipo"]=="PF","saldo_devedor"].sum()
    saldo_pj_total = df.loc[df["tipo"]=="PJ","saldo_devedor"].sum()
    
    alvo_pf = taxa_pf * saldo_pf_total
    alvo_pj = taxa_pj * saldo_pj_total
    
    atual_pf = df.loc[(df["tipo"]=="PF") & (df["status"]=="over 90"),"saldo_devedor"].sum()
    atual_pj = df.loc[(df["tipo"]=="PJ") & (df["status"]=="over 90"),"saldo_devedor"].sum()
    
    if atual_pf < alvo_pf:
        candidatos = df[(df["tipo"]=="PF") & (df["status"]=="over 60")]
        saldo_extra = alvo_pf - atual_pf
        acumulado = 0
        for idx, row in candidatos.iterrows():
            if acumulado >= saldo_extra:
                break
            df.at[idx,"status"] = "over 90"
            acumulado += row["saldo_devedor"]
    
    if atual_pj < alvo_pj:
        candidatos = df[(df["tipo"]=="PJ") & (df["status"]=="over 60")]
        saldo_extra = alvo_pj - atual_pj
        acumulado = 0
        for idx, row in candidatos.iterrows():
            if acumulado >= saldo_extra:
                break
            df.at[idx,"status"] = "over 90"
            acumulado += row["saldo_devedor"]
    
    return df


# -----------------------------
# Amortização mensal
# -----------------------------
def amortizar_operacoes(df):
    df = df.copy()
    # só paga se estiver ativa
    ativa_mask = df["status"] == "ativa"
    df.loc[ativa_mask, "saldo_devedor"] -= df.loc[ativa_mask, "parcela_valor"]
    df.loc[ativa_mask, "parcelas_pagas"] += 1
    # remove operações quitadas
    df = df[df["parcelas_pagas"] < df["parcelas_total"]]
    return df


# -----------------------------
# Cálculo da taxa simulada
# -----------------------------
def calcular_inadimplencia(df):
    saldo_total = df["saldo_devedor"].sum()
    saldo_over90 = df.loc[df["status"]=="over 90","saldo_devedor"].sum()
    return saldo_over90 / saldo_total if saldo_total > 0 else 0


# -----------------------------
# Simulação de 24 meses
# -----------------------------
operacoes = pd.DataFrame()

for mes in range(1, 40):
    # amortiza carteira existente
    if not operacoes.empty:
        operacoes = amortizar_operacoes(operacoes)
    
    # gera novas concessões
    concessoes_pf = 10_000_000 + mes * 100_000
    concessoes_pj = 20_000_000 + mes * 200_000
    novas_op = gerar_operacoes_mes(concessoes_pf, concessoes_pj)
    operacoes = pd.concat([operacoes, novas_op], ignore_index=True)
    
    # aplica inadimplência
    taxa_pf = 0.05
    taxa_pj = 0.03
    operacoes = atualizar_inadimplencia(operacoes, taxa_pf, taxa_pj)
    
    # resumo
    totais_status = operacoes.groupby("status")["saldo_devedor"].sum()
    taxa_simulada = calcular_inadimplencia(operacoes)
    
    print(f"\n=== Mês {mes} ===")
    print("Totais por status:")
    print(totais_status)
    print(f"Taxa simulada over 90: {taxa_simulada:.2%} | Taxa oficial PF: {taxa_pf:.0%} | PJ: {taxa_pj:.0%}")

operacoes.to_excel('teste.xlsx')