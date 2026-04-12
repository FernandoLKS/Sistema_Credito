import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def simular_mes(clientes_pf, clientes_pj, inad_bcb_pf, inad_bcb_pj):
    rng = np.random.default_rng()

    # Calibração PF
    fator_pf = inad_bcb_pf / clientes_pf['pd'].mean()
    pd_pf = np.clip(clientes_pf['pd'] * fator_pf, 0, 1)
    
    pagamentos_pf = rng.binomial(1, 1 - pd_pf)
    inad_pf = 1 - pagamentos_pf.mean()

    # Calibração PJ
    fator_pj = inad_bcb_pj / clientes_pj['pd'].mean()
    pd_pj = np.clip(clientes_pj['pd'] * fator_pj, 0, 1)
    pagamentos_pj = rng.binomial(1, 1 - pd_pj)
    inad_pj = 1 - pagamentos_pj.mean()

    return {
        "inad_pf": inad_pf,
        "inad_pj": inad_pj,
        "total_inad": (inad_pf * len(clientes_pf) + inad_pj * len(clientes_pj)) / (len(clientes_pf) + len(clientes_pj))
    }