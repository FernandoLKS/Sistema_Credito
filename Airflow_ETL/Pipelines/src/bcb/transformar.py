def transformar(df):
    df['credito_total'] = df['credito_total'] * 10
    df['credito_pf'] = df['credito_pf'] * 10
    df['credito_pj'] = df['credito_pj'] * 10

    df['concessoes_total'] = df['concessoes_total'] * 10
    df['concessoes_pf'] = df['concessoes_pf'] * 10
    df['concessoes_pj'] = df['concessoes_pj'] * 10

    return df
