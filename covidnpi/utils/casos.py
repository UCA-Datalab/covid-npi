import datetime as dt
import warnings

import numpy as np
import pandas as pd

from covidnpi.utils.regions import CODE_TO_POBLACION
from covidnpi.utils.log import logger

warnings.filterwarnings("ignore", category=RuntimeWarning)


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
    logger.debug("Loading incidence data")

    def dateparse(x):
        """This function is used to parse the dates of casos"""
        return dt.datetime.strptime(x, "%Y-%m-%d")

    casos = pd.read_csv(link, parse_dates=["fecha"], date_parser=dateparse)

    # Correct some abbreviations
    casos["provincia_iso"] = casos["provincia_iso"].replace({"ME": "ML", "NC": "NA"})
    logger.debug("Done loading incidence data")
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
    pandas.Series
        Total cases of COVID per date

    """
    # Query target province
    casos_sub = casos.query(f"provincia_iso == '{code}'")
    series = casos_sub.set_index("fecha")["num_casos"]

    # Fill missing dates with NaN
    try:
        idx = pd.date_range(series.index.min(), series.index.max())
    except ValueError:
        raise KeyError(f"{code} is not a valid province code")
    series = series.reindex(idx, fill_value=np.nan)
    return series


def return_casos_of_provincia_normed(
    casos: pd.DataFrame,
    code: str,
    per_inhabitants: int = 100000,
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

    Returns
    -------
    pandas.Series
        Cases of COVID per date, per N inhabitants

    """
    series = return_casos_of_provincia(casos, code)
    pob = CODE_TO_POBLACION[code]
    return per_inhabitants * series / pob
