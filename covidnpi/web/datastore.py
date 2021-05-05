import datetime as dt
import os

import pandas as pd
import typer

from covidnpi.utils.casos import (
    load_casos_df,
    return_casos_of_provincia_normed,
)
from covidnpi.utils.config import load_config
from covidnpi.utils.log import logger
from covidnpi.utils.series import cumulative_incidence, compute_growth_rate
from covidnpi.utils.taxonomia import return_taxonomia, PATH_TAXONOMIA
from covidnpi.web.mongo import load_mongo


def store_scores_in_mongo(
    path_output: str = "output/score_ambito",
    path_taxonomia: str = PATH_TAXONOMIA,
    path_config: str = "covidnpi/config.toml",
):
    """Store NPI scores in mongo server

    Parameters
    ----------
    path_output : str, optional
        Path containing the outputs, that we want to store in mongo
    path_taxonomia : str, optional
        Path to taxonomia file
    path_config : str, optional
        Config file contains the route and credentials of mongo server

    """

    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    provincia_to_code = load_config(path_config, key="provincia_to_code")

    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia)
    list_ambito = taxonomia["ambito"].unique().tolist()
    # Get the minimum date in datetime format
    date_min = dt.datetime.strptime(cfg_mongo["date_min"], "%d-%m-%Y")

    for file in os.listdir(path_output):
        path_file = os.path.join(path_output, file)
        df = pd.read_csv(path_file, index_col="fecha")
        # Filter dates previous to the minimum date
        mask_date = pd.to_datetime(df.index, format="%Y-%m-%d") >= date_min
        df = df[mask_date]
        provincia = file.split(".")[0]
        try:
            dict_provincia = {
                "provincia": provincia,
                "code": provincia_to_code[provincia],
                "fechas": df.index.tolist(),
            }
        except KeyError:
            logger.debug(f"\nProvincia '{provincia}' code not found\n")
            continue
        logger.debug(f"\n{provincia}")
        for ambito in list_ambito:
            logger.debug(f"  {ambito}")
            series = df[ambito].values.tolist()
            dict_provincia.update({ambito: series})

        try:
            col = mongo.get_col("scores")
            dict_found = col.find_one({"provincia": provincia})
            _ = dict_found["fechas"]
            mongo.update_dict("scores", "provincia", provincia, dict_provincia)
        except TypeError:
            _ = mongo.insert_new_dict("scores", dict_provincia)


def store_casos_in_mongo(path_config: str = "covidnpi/config.toml"):
    """Store incidence and growth rate in mongo

    Parameters
    ----------
    path_config : str, optional
        Config file contains the route and credentials of mongo server

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    cfg_casos = load_config(path_config, key="casos")

    casos = load_casos_df(link=cfg_casos["link"])
    list_code = casos["provincia_iso"].dropna().unique()
    # Get the minimum date in datetime format
    date_min = dt.datetime.strptime(cfg_mongo["date_min"], "%d-%m-%Y")

    for code in list_code:
        dict_provincia = {}
        try:
            series = return_casos_of_provincia_normed(
                casos, code, path_config=path_config
            )
            # Filter dates previous to the minimum date
            mask_date = series.index >= date_min
            series = series[mask_date]
            logger.debug(f"{code}")
        except KeyError:
            logger.warning(f"{code} missing from poblacion")
            continue
        num = cumulative_incidence(series, cfg_casos["movavg"]).fillna(0)
        growth = compute_growth_rate(series, cfg_casos["movavg"]).fillna(0)
        fechas = [d.strftime("%Y-%m-%d") for d in num.index.tolist()]
        dict_provincia.update(
            {
                "code": code,
                "fechas": fechas,
                "casos": num.values.tolist(),
                "crecimiento": growth.values.tolist(),
            }
        )

        try:
            col = mongo.get_col("casos")
            dict_found = col.find_one({"code": code})
            _ = dict_found["fechas"]
            mongo.update_dict("casos", "code", code, dict_provincia)
        except TypeError:
            _ = mongo.insert_new_dict("casos", dict_provincia)


def datastore(
    path_output: str = "output/score_ambito",
    path_taxonomia: str = PATH_TAXONOMIA,
    path_config: str = "covidnpi/config.toml",
):
    """Stores the data contained in the output folder in mongo

    Parameters
    ----------
    path_output : str, optional
        Path where the output of the preprocess_and_score script is located
    path_taxonomia : str, optional
        Path to taxonomia xlsx file
    path_config : str, optional
        Path to the config toml file

    """
    logger.debug("\n-----\nStoring scores in mongo\n-----\n")
    store_scores_in_mongo(
        path_output=path_output, path_taxonomia=path_taxonomia, path_config=path_config
    )
    logger.debug("\n-----\nStoring number of cases in mongo\n-----\n")
    store_casos_in_mongo(path_config=path_config)


if __name__ == "__main__":
    typer.run(datastore)
