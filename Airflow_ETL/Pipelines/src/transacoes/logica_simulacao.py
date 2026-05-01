import sys
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from criacao_clientes import gerar_clientes_pf, gerar_clientes_pj
from criacao_operacoes import gerar_operacoes_mes
from criacao_transacoes import gerar_transacoes

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
# )
from ....Funcoes.DataBase.conexoes import executar_sql, load_sql

def simulacao():
    query = load_sql("Data_mais_recente.sql")
    print(executar_sql(query))

simulacao()