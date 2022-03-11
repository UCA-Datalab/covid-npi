import json
import os

import pandas as pd
from covidnpi.utils.log import logger


def update_keep_old_keys(dict_old: dict, dict_add: dict, label: str = "_isla") -> dict:
    """Updates a dictionary, but if the same keys are found, keep old ones with a label

    Parameters
    ----------
    dict_old : dict
        Dictionary to update
    dict_add : dict
        Dictionary with new information
    label : str, optional
        Label of old keys, by default "_isla"

    Returns
    -------
    dict
        Updated dictionary
    """
    dict_new = dict_old.copy()
    for key, _ in dict_add.items():
        if key in dict_old.keys():
            dict_new[key + label] = dict_new.pop(key)
    dict_new.update(dict_add)
    return dict_new


def extract_codes_to_dict(df: pd.DataFrame, category: str):
    df_sub = df[df["Nombre TM"] == category]
    d = pd.Series(df_sub["Literal"].values, index=df_sub["Código"]).to_dict()
    return d


def store_dict_provincia_to_interventions(
    dict_interventions, path_output: str = "../output/interventions"
):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_intervention in dict_interventions.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        # Remove file if it exist
        if os.path.exists(path_file):
            os.remove(path_file)
        # Store new file
        df_intervention.to_csv(path_file, index=False)


def load_dict_interventions(path_interventions: str = "output/interventions"):
    dict_interventions = {}
    list_files = os.listdir(path_interventions)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_interventions, file)
        df = pd.read_csv(path_file)
        dict_interventions.update({provincia: df})
    return dict_interventions


def store_dict_scores(dict_scores, path_output: str = "output/interventions"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_score in dict_scores.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        try:
            df_score.to_csv(path_file, float_format="%.3f")
        except AttributeError as er:
            logger.error(f"Provincia {provincia} no puede guardarse: {er}")


def load_dict_scores(path_scores: str = "output/interventions"):
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
    """Guarda un json con las condiciones aplicadas por la taxonomy"""
    if path_output is None:
        return
    with open(path_output, "w") as f:
        json.dump(dict_condicion, f)
