SELECT 
    inadimplencia_pf_mais_90dias, 
    inadimplencia_pj_mais_90dias,
    concessoes_pf,
    concessoes_pj
FROM bcb_macro
WHERE data = %s