import datetime as dt
import warnings

import numpy as np
import pandas as pd
from covidnpi.utils.log import logger
from covidnpi.utils.regions import (
    ISOPROV_REASSIGN,
    ISOPROV_TO_POBLACION,
    ISOPROV_TO_PROVINCIA,
)

warnings.filterwarnings("ignore", category=RuntimeWarning)


def load_cases_df(
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
    logger.debug("Loading cases data")

    def dateparse(x):
        """This function is used to parse the dates of cases"""
        return dt.datetime.strptime(x, "%Y-%m-%d")

    cases = pd.read_csv(
        link,
        parse_dates=["fecha"],
        date_parser=dateparse,
        keep_default_na=False,
        na_values=["NC"],
    )
    # Correct some abbreviations
    cases["provincia_iso"] = (
        cases["provincia_iso"].fillna("Desconocido").replace(ISOPROV_REASSIGN)
    )

    # List abbreviations not appearing in province codes
    list_miss = set(cases["provincia_iso"].unique()) - set(ISOPROV_TO_PROVINCIA.keys())
    if len(list_miss) > 0:
        logger.warning(
            f"The following codes are not assigned to any province: {','.join(list_miss)}"
        )
    # List provinces not appearing in cases
    list_miss = set(ISOPROV_TO_PROVINCIA.keys()) - set(cases["provincia_iso"].unique())
    if len(list_miss) > 0:
        logger.warning(f"The following provinces are missing: {','.join(list_miss)}")

    logger.debug("Done loading cases data")
    return cases


def return_cases_of_provincia(cases: pd.DataFrame, code: str) -> pd.Series:
    """Return the series of total cases of COVID per date, for a province

    Parameters
    ----------
    cases : pandas.DataFrame
        The dataframe returned by load_cases_df
    code : str
        Code of the province (example: "M" for "Madrid")

    Returns
    -------
    pandas.Series
        Total cases of COVID per date

    """
    # Query target province
    cases_sub = cases.query(f"provincia_iso == '{code}'")
    series = cases_sub.set_index("fecha")["num_casos"]

    # Fill missing dates with NaN
    try:
        idx = pd.date_range(series.index.min(), series.index.max())
    except ValueError:
        raise KeyError(f"{code} is not a valid province code")
    series = series.reindex(idx, fill_value=np.nan)
    return series


def return_cases_of_provincia_normed(
    cases: pd.DataFrame,
    code: str,
    per_inhabitants: int = 100000,
) -> pd.Series:
    """Return the series of cases of COVID per date, per N inhabitants,
    for a province

    Parameters
    ----------
    cases : pandas.DataFrame
        The dataframe returned by load_cases_df
    code : str
        Code of the province (example: "M" for "Madrid")
    per_inhabitants : int, optional
        Normalization value, N, by default 100,000

    Returns
    -------
    pandas.Series
        Cases of COVID per date, per N inhabitants

    """
    series = return_cases_of_provincia(cases, code)
    pob = ISOPROV_TO_POBLACION[code]
    return per_inhabitants * series / pob
