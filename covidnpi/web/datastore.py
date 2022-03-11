import datetime as dt
from pathlib import Path

import pandas as pd
import typer
from covidnpi.utils.config import load_config
from covidnpi.utils.log import logger
from covidnpi.utils.regions import PROVINCIA_TO_ISOPROV
from covidnpi.utils.taxonomia import PATH_TAXONOMY, return_taxonomia
from covidnpi.web.mongo import load_mongo


def store_scores_in_mongo(
    path_output: Path = Path("output/score_ambito"),
    path_taxonomia: str = PATH_TAXONOMY,
    path_config: str = "covidnpi/config.toml",
):
    """Store NPI scores in mongo server

    Parameters
    ----------
    path_output : Path, optional
        Path containing the outputs, that we want to store in mongo
    path_taxonomia : str, optional
        Path to taxonomia file
    path_config : str, optional
        Config file contains the route and credentials of mongo server

    """

    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia)
    list_ambito = taxonomia["ambito"].unique().tolist()
    # Get the minimum date in datetime format
    date_min = dt.datetime.strptime(cfg_mongo["date_min"], "%d-%m-%Y")

    for path_file in path_output.iterdir():
        df = pd.read_csv(path_file, index_col="fecha")
        # Filter dates previous to the minimum date
        mask_date = pd.to_datetime(df.index, format="%Y-%m-%d") >= date_min
        df = df[mask_date]
        provincia = path_file.stem
        try:
            dict_provincia = {
                "provincia": provincia,
                "code": PROVINCIA_TO_ISOPROV[provincia],
                "fechas": df.index.tolist(),
            }
        except KeyError:
            logger.debug(
                f"\nProvincia '{provincia}' code not found. Not stored in mongo.\n"
            )
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


def store_casos_in_mongo(
    path_output: Path = Path("output"),
    path_config: str = "covidnpi/config.toml",
):
    """Store incidence and growth rate in mongo

    Parameters
    ----------
    path_output : Path, optional
        Path where the output is located
    path_config : str, optional
        Config file contains the route and credentials of mongo server

    """
    # Initialize mongo
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    # Load Cumulative Incidence and Growth Rate
    cfg_casos = load_config(path_config, key="casos")
    days = cfg_casos["movavg"]
    df_cuminc = pd.read_csv(
        path_output / f"incidencia_acumulada_{days}.csv", index_col=0, parse_dates=True
    )
    df_growth = pd.read_csv(
        path_output / f"incidencia_crecimiento_{days}.csv",
        index_col=0,
        parse_dates=True,
    )

    # Get the minimum date in datetime format
    date_min = dt.datetime.strptime(cfg_mongo["date_min"], "%d-%m-%Y")

    # Loop through province codes
    for code, ser_cuminc in df_cuminc.iteritems():
        logger.debug(f"{code}")
        # Filter dates previous to the minimum date
        mask_date = ser_cuminc.index >= date_min
        ser_cuminc = ser_cuminc[mask_date].copy()
        # Get growth rate, filtered by date
        ser_growth = df_growth.loc[mask_date, code].copy()
        # Get dates in string format
        fechas = [d.strftime("%Y-%m-%d") for d in ser_cuminc.index.tolist()]
        # Define the dictionary to store in mongo
        dict_provincia = {
            "code": code,
            "fechas": fechas,
            "casos": ser_cuminc.values.tolist(),
            "crecimiento": ser_growth.values.tolist(),
        }
        # Store the information in mongo
        try:
            col = mongo.get_col("casos")
            dict_found = col.find_one({"code": code})
            _ = dict_found["fechas"]
            mongo.update_dict("casos", "code", code, dict_provincia)
        except TypeError:
            _ = mongo.insert_new_dict("casos", dict_provincia)


def datastore(
    path_output: str = "output",
    path_taxonomia: str = PATH_TAXONOMY,
    path_config: str = "covidnpi/config.toml",
):
    """Stores the data contained in the output folder in mongo

    Parameters
    ----------
    path_output : str, optional
        Path where the output is located
    path_taxonomia : str, optional
        Path to taxonomia xlsx file
    path_config : str, optional
        Path to the config toml file
    path_regions : str, optional
        Path to the regions file

    """
    path_output = Path(path_output)
    logger.debug("\n-----\nStoring scores in mongo\n-----\n")
    store_scores_in_mongo(
        path_output=path_output / "score_ambito",
        path_taxonomia=path_taxonomia,
        path_config=path_config,
    )
    logger.debug("\n-----\nStoring number of cases in mongo\n-----\n")
    store_casos_in_mongo(path_output=path_output, path_config=path_config)


if __name__ == "__main__":
    typer.run(datastore)
