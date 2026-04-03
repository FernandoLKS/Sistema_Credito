import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Função para ler dados da API da BCB
def get_bcb_series(codigo, data_inicial='01/01/2020', data_final=datetime.today().strftime('%d/%m/%Y')):
    import requests
    import pandas as pd

    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro na série {codigo}: {response.text}")
        return pd.DataFrame()

    data = response.json()
    df = pd.DataFrame(data)

    if df.empty or "data" not in df.columns:
        print(f"Série {codigo} vazia")
        return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    return df

def gerar_clientes(n_clientes=1000, seed=42):
    np.random.seed(seed)
    
    clientes = []
    
    for i in range(n_clientes):        
        # Tipo
        tipo = np.random.choice(['PF', 'PJ'], p=[0.8, 0.2])
        
        # Score
        if tipo == 'PF':
            score = np.random.normal(600, 100)
        else:
            score = np.random.normal(700, 80)
        score = np.clip(score, 300, 850)
        
        # Renda
        if tipo == 'PF':
            renda = np.random.lognormal(np.log(3000), 0.5)
        else:
            renda = np.random.lognormal(np.log(20000), 0.7)
        
        # Limite
        limite = renda * (score / 600) * np.random.uniform(1.5, 3.0)
        
        # Tempo relacionamento
        tempo_rel = np.random.randint(1, 120)
        
        # Histórico atraso (simples)
        prob_atraso = 1 / (1 + np.exp((score - 600)/50))
        historico_atraso = np.random.rand() < prob_atraso
        
        # -------------------------
        # 🔥 DADOS BRUTOS NOVOS
        # -------------------------
        
        if tipo == 'PF':
            idade = int(np.clip(np.random.normal(35, 12), 18, 80))
            dependentes = np.random.randint(0, 5)
            estado_civil = np.random.choice(
                ['solteiro', 'casado', 'divorciado'], 
                p=[0.5, 0.4, 0.1]
            )
            
            setor = None
            tempo_empresa = np.random.randint(0, 40)
        
        else:
            idade = None
            dependentes = None
            estado_civil = None
            
            setor = np.random.choice([
                'comercio', 'industria', 'servicos'
            ])
            tempo_empresa = np.random.randint(1, 30)
        
        # Saldo atual (uso simples)
        saldo = np.random.uniform(0, limite)
        
        # Quantidade de transações mês
        num_transacoes = int(np.clip(
            np.random.normal(20 if tipo=='PF' else 10, 5),
            1, 100
        ))
        
        # Ticket médio
        ticket_medio = renda / num_transacoes * np.random.uniform(0.5, 1.5)
        
        clientes.append({
            "cliente_id": i,
            "tipo": tipo,
            "score_credito": round(score, 0),
            "renda_mensal": round(renda, 2),
            "limite_credito": round(limite, 2),
            "tempo_relacionamento_meses": tempo_rel,
            "historico_atraso": int(historico_atraso),
            
            # PF
            "idade": idade,
            "dependentes": dependentes,
            "estado_civil": estado_civil,
            
            # PJ
            "setor": setor,
            "tempo_empresa_anos": tempo_empresa,
            
            # comportamento simples
            "saldo_atual": round(saldo, 2),
            "num_transacoes_mes": num_transacoes,
            "ticket_medio": round(ticket_medio, 2)
        })
    
    return pd.DataFrame(clientes)