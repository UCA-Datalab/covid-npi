import os

import pandas as pd
import typer

from covidnpi.casos.compute import (
    load_casos_df,
    return_casos_of_provincia_normed,
    moving_average,
    compute_crecimiento,
)
from covidnpi.utils.config import load_config
from covidnpi.utils.taxonomia import return_taxonomia
from covidnpi.web.mongo import load_mongo


def store_scores_in_mongo(
    path_output: str = "output/score_ambito",
    path_taxonomia="datos_NPI/Taxonomía_07022021.xlsx",
    path_config: str = "covidnpi/config.toml",
):
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    # Remove collection
    mongo.remove_collection("scores")

    provincia_to_code = load_config(path_config, key="provincia_to_code")

    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia)
    list_ambito = taxonomia["ambito"].unique().tolist()

    for file in os.listdir(path_output):
        path_file = os.path.join(path_output, file)
        df = pd.read_csv(path_file, index_col="fecha")
        provincia = file.split(".")[0]
        try:
            dict_provincia = {
                "provincia": provincia,
                "code": provincia_to_code[provincia],
                "fechas": df.index.tolist(),
            }
        except KeyError:
            print(f"\nProvincia '{provincia}' code not found\n")
            continue
        print(f"\n{provincia}")
        for ambito in list_ambito:
            print(f"  {ambito}")
            series = df[ambito].values.tolist()
            dict_provincia.update({ambito: series})
        mongo.insert_new_dict("scores", dict_provincia)


def store_casos_in_mongo(path_config: str = "covidnpi/config.toml"):
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    # Remove collection
    mongo.remove_collection("casos")

    cfg_casos = load_config(path_config, key="casos")

    casos = load_casos_df(link=cfg_casos["link"])
    list_code = casos["provincia_iso"].dropna().unique()

    for code in list_code:
        dict_provincia = {}
        try:
            series = return_casos_of_provincia_normed(
                casos, code, path_config=path_config
            )
            print(f"{code}")
        except KeyError:
            print(f"{code} missing from poblacion")
            continue
        num = moving_average(series, cfg_casos["movavg"])
        growth = compute_crecimiento(series, cfg_casos["movavg"])
        dict_provincia.update(
            {
                "code": code,
                "fechas": num.index.tolist(),
                "casos": num.values.tolist(),
                "crecimiento": growth.values.tolist(),
            }
        )
        mongo.insert_new_dict("casos", dict_provincia)


def main(
    path_output: str = "output/score_ambito",
    path_taxonomia="datos_NPI/Taxonomía_07022021.xlsx",
    path_config: str = "covidnpi/config.toml",
):
    print("\n-----\nStoring scores in mongo\n-----\n")
    store_scores_in_mongo(
        path_output=path_output, path_taxonomia=path_taxonomia, path_config=path_config
    )
    print("\n-----\nStoring number of cases in mongo\n-----\n")
    store_casos_in_mongo(path_config=path_config)


if __name__ == "__main__":
    typer.run(main)
