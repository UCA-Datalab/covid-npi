import os

import pandas as pd
import typer
from covidnpi.utils.cases import (
    load_cases_df,
    return_cases_of_provincia_normed,
)
from covidnpi.utils.log import logger
from covidnpi.utils.regions import (
    ISOPROV_REASSIGN,
    ISOPROV_TO_PROVINCIA_LOWER,
    ISOPROV_TO_PROVINCIA,
)
from covidnpi.utils.rho import compute_rho
from covidnpi.utils.series import compute_growth_rate, cumulative_cases

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
    for i, chunk in enumerate(
        pd.read_csv(
            path_csv,
            parse_dates=["date"],
            dayfirst=False,
            chunksize=chunksize,
            low_memory=False,
        )
    ):
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
    path_output: str = "output/mobility",
):
    """Stores the Google mobility reports in csv format"""

    if not os.path.exists(path_output):
        os.mkdir(path_output)

    mob = load_mobility_report()
    cases = load_cases_df()

    for code in mob["code"].unique():
        # Reassign code if needed
        code = ISOPROV_REASSIGN.get(code, code)
        try:
            provincia = ISOPROV_TO_PROVINCIA[code]
            logger.debug(f"{code} - {provincia}")
        except KeyError:
            logger.warning(f"Omitted {code}")
            continue
        dict_reports = return_reports_of_provincia(mob, code)
        series_cases = return_cases_of_provincia_normed(cases, code)
        series_ia7 = cumulative_cases(series_cases, 7)
        series_growth = compute_growth_rate(series_cases, 7)
        series_rho = compute_rho(series_cases)

        # Store data
        df_store = (
            pd.DataFrame(dict_reports)
            .assign(ia7=series_ia7, growth_rate=series_growth, rho=series_rho)
            .rename_axis("date", axis=0)
        )
        filename = ISOPROV_TO_PROVINCIA_LOWER[code]
        df_store.to_csv(os.path.join(path_output, f"{filename}.csv"))


if __name__ == "__main__":
    typer.run(mobility_report_to_csv)
