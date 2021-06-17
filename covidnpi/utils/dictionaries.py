import json
import os

import pandas as pd


def extract_codes_to_dict(df: pd.DataFrame, category: str):
    df_sub = df[df["Nombre TM"] == category]
    d = pd.Series(df_sub["Literal"].values, index=df_sub["Código"]).to_dict()
    return d


def store_dict_provincia_to_medidas(
    dict_medidas, path_output: str = "../output/medidas"
):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_medida in dict_medidas.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        # Remove file if it exist
        if os.path.exists(path_file):
            os.remove(path_file)
        # Store new file
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
        df_score.to_csv(path_file, float_format="%.3f")


def load_dict_scores(path_scores: str = "output/score_medidas"):
    dict_scores = {}
    list_files = os.listdir(path_scores)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_scores, file)
        df = pd.read_csv(path_file, index_col="fecha")
        dict_scores.update({provincia: df})
    return dict_scores


def reverse_dictionary(d: dict) -> dict:
    reversed_dictionary = {value: key for (key, value) in d.items()}
    return reversed_dictionary


def store_dict_condicion(
    dict_condicion: dict, path_output: str = "output/dict_condicion.json"
):
    """Guarda un json con las condiciones aplicadas por la taxonomia"""
    if path_output is None:
        return
    with open(path_output, "w") as f:
        json.dump(dict_condicion, f)
