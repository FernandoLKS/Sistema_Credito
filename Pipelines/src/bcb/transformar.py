def transformar(df):
    print(df)

    df_final = df[df['inadimplencia_total'].notnull()]
    df_final = df_final.sort_values("data")

    return df_final