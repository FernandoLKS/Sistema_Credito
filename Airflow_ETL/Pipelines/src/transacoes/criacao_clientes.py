import numpy as np
import pandas as pd

"""
PF

Idade
Score
Renda
Comprometimento da Renda
Historico de Atraso
Tempo de Empresa
Patrimonio
Tempo Relacionamento
"""

"""
PJ

Idade
Score
Faturamento Mensal
Margem de Lucro
Alavancagem
Setor
Número de Funcionários
Historico de Atraso
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def gerar_clientes_pf(quantidade: int, seed: int = None):
    rng = np.random.default_rng(seed)

    # idade (normal truncada)
    a, b = (18 - 40)/10, (85 - 40)/10
    idade = stats.truncnorm(a, b, loc=40, scale=10).rvs(size=quantidade, random_state=rng).astype(int)

    # renda (normal truncada + leve cauda à direita)
    a, b = (1200 - 3000)/1000, (80000 - 3000)/1000
    renda_base = stats.truncnorm(a, b, loc=3000, scale=1000).rvs(size=quantidade, random_state=rng)
    renda = renda_base + stats.expon(scale=1500).rvs(size=quantidade, random_state=rng)

    # comprometimento (beta)
    comprometimento = stats.beta(a=2, b=5).rvs(size=quantidade, random_state=rng)

    # histórico de atraso (poisson)
    historico_atraso = stats.poisson(mu=1.5).rvs(size=quantidade, random_state=rng)
    mask_ruim = rng.random(quantidade) < 0.1
    historico_atraso[mask_ruim] += rng.integers(3, 10, size=mask_ruim.sum())

    # tempo de empresa (exponencial limitada pela idade)
    tempo_empresa = stats.expon(scale=5).rvs(size=quantidade, random_state=rng)
    tempo_empresa = np.minimum(tempo_empresa, idade - 18)

    mask = rng.random(quantidade) < 0.25
    tempo_empresa[mask] = rng.integers(0, 5, size=mask.sum())
    tempo_empresa = tempo_empresa.astype(int)

    # patrimônio (proporcional à renda + ruído)
    patrimonio = renda * rng.uniform(3, 25, size=quantidade)
    patrimonio += stats.norm(loc=0, scale=10000).rvs(size=quantidade, random_state=rng)
    patrimonio = np.clip(patrimonio, 0, None)

    # tempo de relacionamento (gamma)
    tempo_relacionamento = stats.gamma(a=2, scale=3).rvs(size=quantidade, random_state=rng)
    tempo_relacionamento = np.minimum(tempo_relacionamento, idade - 18)
    tempo_relacionamento = tempo_relacionamento.astype(int)

    #probablidade de default (modelo + ruído normal)
    def padronizar_z(x):
        return (x - x.mean()) / x.std()
    
    logit = (
        -2
        + 0.8 * padronizar_z(1/idade)
        + 1.5 * padronizar_z(comprometimento)
        + 1.0 * padronizar_z(historico_atraso)
        - 1.2 * padronizar_z(renda)
        - 0.5 * padronizar_z(tempo_empresa)
        + rng.normal(0, 0.3, size=quantidade)
    )

    pdefault = 1 / (1 + np.exp(-logit))

    df = pd.DataFrame({
        "idade": idade,
        "renda": renda,
        "pd": pdefault,
        "comprometimento_renda": comprometimento,
        "historico_atraso": historico_atraso,
        "tempo_empresa": tempo_empresa,
        "patrimonio": patrimonio,
        "tempo_relacionamento": tempo_relacionamento
    })

    return df

def gerar_clientes_pj(quantidade: int, seed: int = None):
    rng = np.random.default_rng(seed)

    # setor da empresa
    setores = ["servicos", "varejo", "industria", "agro", "tech"]
    probs = [0.40, 0.25, 0.15, 0.10, 0.10]
    setor = rng.choice(setores, size=quantidade, p=probs)

    efeito_setor = {
        "servicos": 0.0,
        "varejo": 0.2,
        "industria": 0.3,
        "agro": 0.4,
        "tech": -0.1
    }
    setor_efeito = np.array([efeito_setor[s] for s in setor])

    # idade da empresa (anos)
    idade_empresa = stats.truncnorm(
        (0 - 10) / 5, (50 - 10) / 5,
        loc=10, scale=5
    ).rvs(size=quantidade, random_state=rng).astype(int)

    # número de funcionários (estrutura da empresa)
    base_func = stats.lognorm(s=1, scale=np.exp(3)).rvs(
        size=quantidade, random_state=rng
    )
    num_funcionarios = np.clip(base_func, 1, 20000).astype(int)

    # produtividade por funcionário (depende do setor)
    prod_base = np.array([
        {"servicos": 80_000, "varejo": 60_000, "industria": 120_000,
         "agro": 150_000, "tech": 250_000}[s]
        for s in setor
    ])

    produtividade = stats.lognorm(
        s=0.6,
        scale=prod_base
    ).rvs(random_state=rng)

    # faturamento ANUAL (estrutura × produtividade)
    faturamento = num_funcionarios * produtividade

    # alavancagem financeira
    alavancagem = stats.beta(a=2, b=2).rvs(size=quantidade, random_state=rng)

    # histórico de atraso
    historico_atraso = stats.poisson(mu=1.2).rvs(size=quantidade, random_state=rng)
    mask_ruim = rng.random(quantidade) < 0.08
    historico_atraso[mask_ruim] += rng.integers(3, 8, size=mask_ruim.sum())

    # margem de lucro baseada em eficiência
    escala = np.log(faturamento) - np.log(num_funcionarios + 1)

    margem_lucro = (
        0.05
        + 0.04 * np.tanh(escala)
        + 0.5 * setor_efeito
        + rng.normal(0, 0.05, size=quantidade)
    )
    margem_lucro = np.clip(margem_lucro, -0.2, 0.5)

    # padronização
    def z(x):
        return (x - x.mean()) / (x.std() + 1e-8)

    # probabilidade de inadimplência (PD PJ)
    logit = (
        -2.5
        + 1.3 * z(alavancagem)
        + 1.2 * z(historico_atraso)
        - 1.0 * z(margem_lucro)
        - 0.9 * z(faturamento)
        - 0.5 * z(idade_empresa)
        + setor_efeito
        + rng.normal(0, 0.3, size=quantidade)
    )

    pdefault = 1 / (1 + np.exp(-logit))

    # dataframe final
    df = pd.DataFrame({
        "setor": setor,
        "idade_empresa": idade_empresa,
        "faturamento_anual": faturamento,
        "num_funcionarios": num_funcionarios,
        "margem_lucro": margem_lucro,
        "alavancagem": alavancagem,
        "historico_atraso": historico_atraso,
        "pd": pdefault
    })

    return df