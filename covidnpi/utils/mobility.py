import os

import pandas as pd
import typer

from covidnpi.utils.casos import load_casos_df, return_casos_of_provincia_normed
from covidnpi.utils.config import load_config
from covidnpi.utils.log import logger
from covidnpi.utils.rho import compute_normed_incidence
from covidnpi.utils.series import (
    cumulative_incidence,
    compute_growth_rate,
)

URL_MOBILITY = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"


def load_mobility_report(
    country: str = "ES",
    path_csv: str = URL_MOBILITY,
    chunksize: int = 500000,
) -> pd.DataFrame:
    """Loads the Google mobility report of a certain country. Adds additional columns:
    - code : province code

    Parameters
    ----------
    country : str, optional
        Code of the country to load, by default "ES"
    path_csv : str, optional
        Link or path to the mobility report csv
    chunksize : int, optional
        Rows of data read at once, by default 500000

    Returns
    -------
    pandas.DataFrame
        Mobility report of given country

    """
    logger.debug("Loading mobility report")
    # Process in chunks to not saturate the memory
    df_list = []
    for i, chunk in enumerate(pd.read_csv(
        path_csv,
        parse_dates=["date"],
        dayfirst=False,
        chunksize=chunksize,
        low_memory=False,
    )):
        df_list += [chunk.query(f"country_region_code == '{country}'")]
        logger.debug(f"    Loaded chunk {i}")
    mob = pd.concat(df_list)
    del df_list
    logger.debug("Done loading all chunks. Merged into single dataframe.")

    # Codes of each province
    mob["code"] = mob["iso_3166_2_code"].str.replace(f"{country}-", "")
    logger.debug("Done loading mobility report")
    return mob


def return_reports_of_provincia(mob: pd.DataFrame, code: str) -> dict:
    """Returns a dictionary containing all the reports for a given province

    Parameters
    ----------
    mob : pandas.DataFrame
        Mobility report dataframe
    code : str
        Province code

    Returns
    -------
    dict
        Contains pandas.Series

    """
    df = mob.query(f"code == '{code}'").set_index("date")
    list_reports = [col for col in mob.columns if "percent" in col]
    dict_reports = {}
    for col in list_reports:
        name = col.split("_", 1)[0]
        series = df[col]
        dict_reports.update({name: series})
    return dict_reports


def mobility_report_to_csv(
    path_config: str = "covidnpi/config.toml", path_output: str = "output/mobility"
):
    """Stores the Google mobility reports in csv format"""

    if not os.path.exists(path_output):
        os.mkdir(path_output)

    mob = load_mobility_report()
    casos = load_casos_df()
    code_to_provincia = load_config(path_config, "code_to_provincia")
    provincia_to_code = load_config(path_config, "provincia_to_code")
    code_to_filename = {v: k for k, v in provincia_to_code.items()}

    for code in mob["code"].unique():
        try:
            provincia = code_to_provincia[code]
            logger.debug(f"{code} - {provincia}")
        except KeyError:
            logger.debug(f"Omitted {code}")
            continue
        dict_reports = return_reports_of_provincia(mob, code)
        series_casos = return_casos_of_provincia_normed(
            casos, code, path_config=path_config
        )
        casos_norm = compute_normed_incidence(series_casos)
        print(casos_norm)
        series_ia7 = cumulative_incidence(series_casos, 7)
        series_growth = compute_growth_rate(series_casos, 7)

        # Store data
        df_store = pd.DataFrame(dict_reports).assign(
            ia7=series_ia7, growth_rate=series_growth
        )
        filename = code_to_filename[code]
        df_store.to_csv(os.path.join(path_output, f"{filename}.csv"))


if __name__ == "__main__":
    typer.run(mobility_report_to_csv)
