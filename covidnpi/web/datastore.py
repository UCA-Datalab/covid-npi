import datetime as dt
from pathlib import Path
from xmlrpc.client import ServerProxy

import numpy as np
import pandas as pd
import typer
from covidnpi.utils.config import load_config
from scipy.stats import variation, iqr
from covidnpi.utils.log import logger
from covidnpi.utils.regions import PROVINCIA_TO_ISOPROV
from covidnpi.utils.taxonomy import PATH_TAXONOMY, return_taxonomy
from covidnpi.web.mongo import load_mongo


def store_scores_in_mongo(
    path_output: Path = Path("output/score_field"),
    path_taxonomy: str = PATH_TAXONOMY,
    path_config: str = "covidnpi/config.toml",
):
    """Store NPI scores in mongo server. Format:
    [
        {
            "province": str,
            "code": int,
            "dates": List[str],
            `field`: List[float],
            "mean": {`field`: float},
            "median": {`field`: float},
        }
    ]

    Parameters
    ----------
    path_output : Path, optional
        Path containing the outputs, that we want to store in mongo
    path_taxonomy : str, optional
        Path to taxonomy file
    path_config : str, optional
        Config file contains the route and credentials of mongo server

    """

    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    taxonomy = return_taxonomy(path_taxonomy=path_taxonomy)
    list_field = taxonomy["ambito"].unique().tolist()
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
                "province": provincia,
                "code": PROVINCIA_TO_ISOPROV[provincia],
                "dates": df.index.tolist(),
            }
        except KeyError:
            logger.debug(
                f"\nProvincia '{provincia}' code not found. Not stored in mongo.\n"
            )
            continue
        logger.debug(f"\n{provincia}")

        # Initialize list of statistics
        list_mean = []
        list_median = []
        list_std = []
        list_iqr = []
        list_var = []

        # Loop through fields of activity
        for field in list_field:
            logger.debug(f"  {field}")
            series = df[field].values.tolist()
            dict_provincia.update({field: series})
            # Compute all statistics
            list_mean.append(np.mean(series))
            list_median.append(np.median(series))
            list_std.append(np.std(series))
            list_iqr.append(iqr(series))
            list_var.append(variation(series))

        # Include statistics
        dict_provincia.update(
            {
                "Mean": list_mean,
                "Median": list_median,
                "Standard deviation": list_std,
                "Interquantile range": list_iqr,
                "Coefficient of variation": list_var,
                "fields": [s.replace("_", " ").capitalize() for s in list_field],
            }
        )

        try:
            col = mongo.get_col("scores")
            dict_found = col.find_one({"province": provincia})
            _ = dict_found["dates"]
            mongo.update_dict("scores", "province", provincia, dict_provincia)
        except TypeError:
            _ = mongo.insert_new_dict("scores", dict_provincia)
        except KeyError as er:
            raise KeyError(f"Error in collection 'scores': {er}")


def store_cases_in_mongo(
    path_output: Path = Path("output"),
    path_config: str = "covidnpi/config.toml",
):
    """Store cases and growth rate in mongo

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
    # Load Cumulative cases and Growth Rate
    cfg_cases = load_config(path_config, key="cases")
    days = cfg_cases["movavg"]
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
            "dates": fechas,
            "cases": ser_cuminc.values.tolist(),
            "growth_rate": ser_growth.values.tolist(),
        }
        # Store the information in mongo
        try:
            col = mongo.get_col("cases")
            dict_found = col.find_one({"code": code})
            _ = dict_found["dates"]
            mongo.update_dict("cases", "code", code, dict_provincia)
        except TypeError:
            _ = mongo.insert_new_dict("cases", dict_provincia)
        except KeyError as er:
            raise KeyError(f"Error in collection 'cases': {er}")


def datastore(
    path_output: str = "output",
    path_taxonomy: str = PATH_TAXONOMY,
    path_config: str = "covidnpi/config.toml",
):
    """Stores the data contained in the output folder in mongo

    Parameters
    ----------
    path_output : str, optional
        Path where the output is located
    path_taxonomy : str, optional
        Path to taxonomy xlsx file
    path_config : str, optional
        Path to the config toml file
    path_regions : str, optional
        Path to the regions file

    """
    path_output = Path(path_output)
    logger.debug("\n-----\nStoring scores in mongo\n-----\n")
    store_scores_in_mongo(
        path_output=path_output / "score_field",
        path_taxonomy=path_taxonomy,
        path_config=path_config,
    )
    logger.debug("\n-----\nStoring number of cases in mongo\n-----\n")
    store_cases_in_mongo(path_output=path_output, path_config=path_config)


if __name__ == "__main__":
    typer.run(datastore)
