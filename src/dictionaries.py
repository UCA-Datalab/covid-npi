import pandas as pd


def extract_codes_to_dict(df: pd.DataFrame, category: str):
    df_sub = df[df["Nombre TM"] == category]
    d = pd.Series(df_sub["Literal"].values, index=df_sub["Código"]).to_dict()
    return d