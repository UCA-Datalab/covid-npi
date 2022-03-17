import datetime as dt
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import typer
from adjustText import adjust_text
from covidnpi.utils.cases import load_cases_df, return_cases_of_provincia_normed
from covidnpi.utils.fields import list_fields
from covidnpi.utils.log import logger
from covidnpi.utils.regions import (
    DICT_RENAME_PROVINCIA_LOWER,
    ISOPROV_TO_PROVINCIA,
    PROVINCIA_LOWER_TO_ISOPROV,
)


def dataframe_of_npi_score_mean_by_date_province(path_data: Path) -> pd.DataFrame:
    """Returns a dataframe with the mean NPI score per province (columns)
    and date (rows).

    Parameters
    ----------
    path_data : Path
        Path to the data folder. Must contain the folder "score_field"

    Returns
    -------
    pd.DataFrame
        Dataframe with mean NPI scores, index is datetimes,
        columns are provinces codes.
    """
    # Path to score_field
    path_field = path_data / "score_field"
    # List the fields of interest
    list_amb = list_fields(path_data)
    logger.debug(
        f"Fields of activity used to compute the mean NPI: {', '.join(list_amb)}"
    )
    # Initialize dictionary of fields
    dict_field = {}
    # Loop through each province
    for path_file in path_field.iterdir():
        # Province name
        province = path_file.name.split(".")[0]
        # Mean score by date
        ser = pd.read_csv(path_file, index_col=0)[list_amb].mean(axis=1)
        # Index to datetime
        ser.index = pd.to_datetime(ser.index)
        # Rename province if needed
        province = DICT_RENAME_PROVINCIA_LOWER.get(province, province)
        code = PROVINCIA_LOWER_TO_ISOPROV.get(province, province)
        # Compute the field under the curve and store
        dict_field.update({code: ser})
    return pd.DataFrame.from_dict(dict_field)


def dict_of_npi_score_mean_by_province(
    path_data: Path,
    date_min: str = "15-09-2020",
    date_max: str = "08-05-2021",
) -> Dict:
    """Returns a dictionary that contains the NPI mean score
    of each province.

    Parameters
    ----------
    path_data : Path
        Path to the data folder. Must contain the folder "score_field"
    date_min : str, optional
        Minimum date with format "%d-%m-%Y", by default "15-09-2020"
    date_max : str, optional
        Maximum date with format "%d-%m-%Y", by default "08-05-2021"

    Returns
    -------
    Dict
        Province Code: NPI score field
    """
    df = dataframe_of_npi_score_mean_by_date_province(path_data)
    # String to datetime
    date_min = dt.datetime.strptime(date_min, "%d-%m-%Y")
    date_max = dt.datetime.strptime(date_max, "%d-%m-%Y")
    # Limit dataframe within date range
    df = df[(df.index >= date_min) & (df.index <= date_max)]
    # Initialize dictionary of mean NPI per province
    dict_npi = {}
    # Compute the average NPI per province
    for column in df:
        ser = df[column]
        dict_npi.update({column: ser.mean()})
    return dict_npi


def dataframe_of_cases_by_date_province() -> pd.DataFrame:
    """Returns a dataframe with the daily number of casess
    per province (column) and date (row)

    Returns
    -------
    pd.DataFrame
        Pandas dataframe, index is datetime, columns are provinces codes
    """
    cases = load_cases_df()
    # Initialize dictionary of time series
    dict_ser = {}
    for _, code in PROVINCIA_LOWER_TO_ISOPROV.items():
        # cases by province for each 100,000 inhabitants
        ser = return_cases_of_provincia_normed(cases, code)
        # Index to datetime
        ser.index = pd.to_datetime(ser.index)
        dict_ser.update({code: ser})
    return pd.DataFrame.from_dict(dict_ser)


def dict_of_cases_mean_by_province(
    date_min: str = "15-09-2020",
    date_max: str = "08-05-2021",
) -> Dict:
    """Returns a dictionary that contains the mean number of cases
    of each province.

    Parameters
    ----------
    date_min : str, optional
        Minimum date with format "%d-%m-%Y", by default "15-09-2020"
    date_max : str, optional
        Maximum date with format "%d-%m-%Y", by default "08-05-2021"

    Returns
    -------
    Dict
        Province Code: Mean number of cases
    """
    df = dataframe_of_cases_by_date_province()
    # String to datetime
    date_min = dt.datetime.strptime(date_min, "%d-%m-%Y")
    date_max = dt.datetime.strptime(date_max, "%d-%m-%Y")
    # Limit dataframe within date range
    df = df[(df.index >= date_min) & (df.index <= date_max)]
    # Initialize dictionary of cases per province
    dict_cases = {}
    # Compute the average cases of each province
    for column in df:
        ser = df[column]
        dict_cases.update({column: ser.mean()})
    return dict_cases


def main(
    path_data: str = "output",
    date_min: str = "15-09-2020",
    date_max: str = "08-05-2021",
):
    path_data = Path(path_data)

    # Dictionary of scores and cases
    dict_scores = dict_of_npi_score_mean_by_province(
        path_data, date_min=date_min, date_max=date_max
    )
    dict_infect = dict_of_cases_mean_by_province(date_min=date_min, date_max=date_max)

    # List provinces, scores and cases
    list_provinces = []
    list_scores = []
    list_infect = []
    for province, score in dict_scores.items():
        try:
            cases = dict_infect[province]
        except KeyError:
            logger.warning(f"Province {province} has no infected value. Skipped.")
            continue
        list_provinces.append(province)
        list_scores.append(score)
        list_infect.append(cases)

    # Scatter plot of NPI vs cases
    plt.figure(dpi=160)
    plt.scatter(
        list_scores,
        list_infect,
        c=np.multiply(list_infect, list_scores),
        label="Data points",
    )
    # Plot lines in medians
    plt.axhline(np.median(list_infect), linestyle="--", color="k", alpha=0.3)
    plt.axvline(np.median(list_scores), linestyle="--", color="k", alpha=0.3)

    # Compute correlation
    r = np.corrcoef(list_scores, list_infect)[0, 1]
    plt.scatter([], [], c="w", alpha=1, label=f"Pearson's r = {round(r,2)}")
    plt.legend()

    # Include the provinces codes, adjusted so that they do not overlap
    list_text = []
    for idx, code in enumerate(list_provinces):
        list_text.append(
            plt.text(
                list_scores[idx],
                list_infect[idx],
                ISOPROV_TO_PROVINCIA[code],
                fontdict={"size": 7},
            )
        )
    adjust_text(list_text, arrowprops=dict(arrowstyle="->", color="grey", lw=0.5))

    # Labels and store the image
    plt.xlabel("Mean stringency index")
    plt.ylabel("Cases per day (100,000 inhabitants)")
    plt.savefig(path_data / "npi_vs_cases.png")


if __name__ == "__main__":
    typer.run(main)
