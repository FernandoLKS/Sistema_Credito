from Pipelines.src.transacoes.criacao_transacoes import gerar_transacoes

def rodar_simulacao(data_ref, clientes, operacoes, informacoes_bcb):
    taxa_pf_bcb = informacoes_bcb.loc[0, 'inadimplencia_pf_mais_90dias']
    taxa_pj_bcb = informacoes_bcb.loc[0, 'inadimplencia_pj_mais_90dias']
    concessoes_pf = informacoes_bcb.loc[0, 'concessoes_pf']
    concessoes_pj = informacoes_bcb.loc[0, 'concessoes_pj']

    clientes["removido"] = clientes["removido"].fillna(False).astype(bool)
    clientes["inativo_meses"] = clientes["inativo_meses"].fillna(0).astype(int)

    resultado = gerar_transacoes(
        data_ref=data_ref,
        clientes=clientes,
        operacoes=operacoes,
        concessoes_pf=concessoes_pf,
        concessoes_pj=concessoes_pj,
        taxa_pf_bcb=taxa_pf_bcb,
        taxa_pj_bcb=taxa_pj_bcb
    )

    return resultado