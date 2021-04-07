import os

import pandas as pd

from covidnpi.utils.casos import load_casos_df, return_casos_of_provincia_normed
from covidnpi.utils.config import load_config
from covidnpi.utils.series import (
    cumulative_incidence,
    compute_growth_rate,
)

URL_MOBILITY = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"


def load_mobility_report(
    country: str = "ES", path_csv: str = URL_MOBILITY
) -> pd.DataFrame:
    """Loads the Google mobility report of a certain country. Adds additional columns:
    - code : province code

    Parameters
    ----------
    country : str, optional
        Code of the country to load, by default "ES"
    path_csv : str, optional
        Link or path to the mobility report csv

    Returns
    -------
    pandas.DataFrame
        Mobility report of given country

    """
    # Process in chunks to not saturate the memory
    df_list = []
    for chunk in pd.read_csv(
        path_csv, parse_dates=["date"], dayfirst=False, chunksize=5e5, low_memory=False
    ):
        df_list += [chunk.query(f"country_region_code == '{country}'")]
    mob = pd.concat(df_list)
    del df_list

    # Codes of each province
    mob["code"] = mob["iso_3166_2_code"].str.replace(f"{country}-", "")
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
    path_config: str = "../config.toml", path_output: str = "../output/mobility"
):
    """Stores the Google mobility reports in csv format"""

    if not os.path.exists(path_output):
        os.mkdir(path_output)

    mob = load_mobility_report()
    casos = load_casos_df()
    code_to_provincia = load_config(path_config, "code_to_provincia")

    for code in mob["code"].unique():
        try:
            provincia = code_to_provincia[code]
            print(f"{code} - {provincia}")
        except KeyError:
            print(f"Omitted {code}")
            continue
        dict_reports = return_reports_of_provincia(mob, code)
        series_casos = return_casos_of_provincia_normed(
            casos, code, path_config=path_config
        )
        series_ia7 = cumulative_incidence(series_casos, 7)
        series_growth = compute_growth_rate(series_casos, 7)

        # Store data
        df_store = pd.DataFrame(dict_reports).assign(
            ia7=series_ia7, growth_rate=series_growth
        )
        df_store.to_csv(os.path.join(path_output, f"{code}.csv"))
