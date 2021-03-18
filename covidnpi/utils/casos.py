import datetime as dt
import warnings

import numpy as np
import pandas as pd

from covidnpi.utils.config import load_config

warnings.filterwarnings("ignore", category=RuntimeWarning)


def _dateparse(x):
    """This function is used to parse the dates of casos"""
    return dt.datetime.strptime(x, "%Y-%m-%d")


def load_casos_df(
    link: str = "https://cnecovid.isciii.es/covid19/resources/"
    "casos_tecnica_provincia.csv",
) -> pd.DataFrame:
    """Loads a dataframe containing the number of COVID cases by day and province

    Parameters
    ----------
    link : str, optional
        Web link

    Returns
    -------
    pandas.DataFrame
        Number of cases of COVID by day and province

    """

    casos = pd.read_csv(link, parse_dates=["fecha"], date_parser=_dateparse)

    # Correct some abbreviations
    casos["provincia_iso"] = casos["provincia_iso"].replace({"ME": "ML", "NC": "NA"})

    return casos


def return_casos_of_provincia(casos: pd.DataFrame, code: str) -> pd.Series:
    """Return the series of total cases of COVID per date, for a province

    Parameters
    ----------
    casos : pandas.DataFrame
        The dataframe returned by load_casos_df
    code : str
        Code of the province (example: "M" for "Madrid")

    Returns
    -------
    pandas.Series        Total c+ases of COVID per date

    """
    # Query target province
    casos_sub = casos.query(f"provincia_iso == '{code}'")
    series = casos_sub.set_index("fecha")["num_casos"]

    # Fill missing dates with NaN
    idx = pd.date_range(series.index.min(), series.index.max())
    series = series.reindex(idx, fill_value=np.nan)
    return series


def return_casos_of_provincia_normed(
    casos: pd.DataFrame,
    code: str,
    per_inhabitants: int = 100000,
    path_config: str = "covidnpi/config.toml",
) -> pd.Series:
    """Return the series of cases of COVID per date, per N inhabitants,
    for a province

    Parameters
    ----------
    casos : pandas.DataFrame
        The dataframe returned by load_casos_df
    code : str
        Code of the province (example: "M" for "Madrid")
    per_inhabitants : int, optional
        Normalization value, N, by default 100,000
    path_config : str, optional
        Path to the config file, by default "covidnpi/config.toml"

    Returns
    -------
    pandas.Series
        Cases of COVID per date, per N inhabitants

    """
    series = return_casos_of_provincia(casos, code)
    code_to_poblacion = load_config(path_config, "code_to_poblacion")
    pob = code_to_poblacion[code]
    return per_inhabitants * series / pob
