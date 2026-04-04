Criar_tabela_bcb_macro = """
CREATE TABLE IF NOT EXISTS bcb_macro (
    data DATE PRIMARY KEY,
    
    inadimplencia_total DECIMAL(5,2),
    inadimplencia_pf DECIMAL(5,2),
    inadimplencia_pj DECIMAL(5,2),
    inadimplencia_30 DECIMAL(5,2),
    inadimplencia_60 DECIMAL(5,2),
    
    credito_vencido_pf DECIMAL(5,2),
    credito_vencido_pj DECIMAL(5,2),
    
    juros_credito DECIMAL(5,2),
    spread_bancario DECIMAL(5,2),
    
    credito_total DECIMAL(12,2),
    credito_pf DECIMAL(12,2),
    credito_pj DECIMAL(12,2),
    novo_credito_pf DECIMAL(12,2),
    novo_credito_pj DECIMAL(12,2),
    qtde_contratos DECIMAL(7,2),
    
    selic DECIMAL(5,2),
    ipca DECIMAL(5,2)
);
"""
