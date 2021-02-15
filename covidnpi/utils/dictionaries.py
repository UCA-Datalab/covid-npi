import os

import pandas as pd


def extract_codes_to_dict(df: pd.DataFrame, category: str):
    df_sub = df[df["Nombre TM"] == category]
    d = pd.Series(df_sub["Literal"].values, index=df_sub["Código"]).to_dict()
    return d


def store_dict_medidas(dict_medidas, path_output: str = "../output/medidas"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_medida in dict_medidas.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        df_medida = df_medida[
            [
                "comunidad_autonoma",
                "provincia",
                "codigo",
                "fecha_inicio",
                "fecha_fin",
                "fecha_publicacion_oficial",
                "ambito",
                "porcentaje_afectado",
                "porcentaje",
                "personas",
                "hora",
                "nivel_educacion",
            ]
        ]
        df_medida.to_csv(path_file, index=False)


def load_dict_medidas(path_medidas: str = "output/medidas"):
    dict_medidas = {}
    list_files = os.listdir(path_medidas)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_medidas, file)
        df = pd.read_csv(path_file)
        dict_medidas.update({provincia: df})
    return dict_medidas


def store_dict_scores(dict_scores, path_output: str = "output/score_medidas"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_score in dict_scores.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        df_score.to_csv(path_file, float_format='%.3f')


def load_dict_scores(path_scores: str = "output/score_medidas"):
    dict_scores = {}
    list_files = os.listdir(path_scores)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_scores, file)
        df = pd.read_csv(path_file, index_col="fecha")
        dict_scores.update({provincia: df})
    return dict_scores
