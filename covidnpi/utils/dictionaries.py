import os

import pandas as pd


def extract_codes_to_dict(df: pd.DataFrame, category: str):
    df_sub = df[df["Nombre TM"] == category]
    d = pd.Series(df_sub["Literal"].values, index=df_sub["Código"]).to_dict()
    return d


def store_dict_scores(dict_scores, path_output: str = "output/score_medidas"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_score in dict_scores.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        df_score.to_csv(path_file)


def load_dict_scores(path_scores: str = "output/score_medidas"):
    dict_scores = {}
    list_files = os.listdir(path_scores)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_scores, file)
        df = pd.read_csv(path_file)
        dict_scores.update({provincia: df})
    return dict_scores
