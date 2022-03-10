import datetime as dt
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import typer
from adjustText import adjust_text
from covidnpi.utils.ambitos import list_ambitos
from covidnpi.utils.casos import load_casos_df, return_casos_of_provincia_normed
from covidnpi.utils.log import logger
from covidnpi.utils.regions import (
    ISOPROV_TO_PROVINCIA,
    DICT_PROVINCE_RENAME,
    PROVINCIA_TO_ISOPROV,
)


def dataframe_of_npi_score_mean_by_date_province(path_data: Path) -> pd.DataFrame:
    """Returns a dataframe with the mean NPI score per province (columns)
    and date (rows).

    Parameters
    ----------
    path_data : Path
        Path to the data folder. Must contain the folder "score_ambito"

    Returns
    -------
    pd.DataFrame
        Dataframe with mean NPI scores, index is datetimes,
        columns are provinces codes.
    """
    # Path to score_ambito
    path_area = path_data / "score_ambito"
    # List the ambitos of interest
    list_amb = list_ambitos(path_data)
    logger.debug(
        f"Fields of activity used to compute the mean NPI: {', '.join(list_amb)}"
    )
    # Initialize dictionary of areas
    dict_ambito = {}
    # Loop through each province
    for path_file in path_area.iterdir():
        # Province name
        province = path_file.name.split(".")[0]
        # Mean score by date
        ser = pd.read_csv(path_file, index_col=0)[list_amb].mean(axis=1)
        # Index to datetime
        ser.index = pd.to_datetime(ser.index)
        # Rename province if needed
        province = DICT_PROVINCE_RENAME.get(province, province)
        code = PROVINCIA_TO_ISOPROV.get(province, province)
        # Compute the area under the curve and store
        dict_ambito.update({code: ser})
    return pd.DataFrame.from_dict(dict_ambito)


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
        Path to the data folder. Must contain the folder "score_ambito"
    date_min : str, optional
        Minimum date with format "%d-%m-%Y", by default "15-09-2020"
    date_max : str, optional
        Maximum date with format "%d-%m-%Y", by default "08-05-2021"

    Returns
    -------
    Dict
        Province Code: NPI score area
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


def dataframe_of_infection_by_date_province() -> pd.DataFrame:
    """Returns a dataframe with the daily number of infections
    per province (column) and date (row)

    Returns
    -------
    pd.DataFrame
        Pandas dataframe, index is datetime, columns are provinces codes
    """
    casos = load_casos_df()
    # Initialize dictionary of time series
    dict_ser = {}
    for _, code in PROVINCIA_TO_ISOPROV.items():
        # Incidence by province for each 100,000 inhabitants
        ser = return_casos_of_provincia_normed(casos, code)
        # Index to datetime
        ser.index = pd.to_datetime(ser.index)
        dict_ser.update({code: ser})
    return pd.DataFrame.from_dict(dict_ser)


def dict_of_infection_mean_by_province(
    date_min: str = "15-09-2020",
    date_max: str = "08-05-2021",
) -> Dict:
    """Returns a dictionary that contains the infection mean
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
        Province Code: Infection area
    """
    df = dataframe_of_infection_by_date_province()
    # String to datetime
    date_min = dt.datetime.strptime(date_min, "%d-%m-%Y")
    date_max = dt.datetime.strptime(date_max, "%d-%m-%Y")
    # Limit dataframe within date range
    df = df[(df.index >= date_min) & (df.index <= date_max)]
    # Initialize dictionary of infection per province
    dict_infection = {}
    # Compute the average infection of each province
    for column in df:
        ser = df[column]
        dict_infection.update({column: ser.mean()})
    return dict_infection


def main(
    path_data: str = "output",
    date_min: str = "15-09-2020",
    date_max: str = "08-05-2021",
):
    path_data = Path(path_data)

    # Dictionary of scores and infection
    dict_scores = dict_of_npi_score_mean_by_province(
        path_data, date_min=date_min, date_max=date_max
    )
    dict_infect = dict_of_infection_mean_by_province(
        date_min=date_min, date_max=date_max
    )

    # List provinces, scores and infection
    list_provinces = []
    list_scores = []
    list_infect = []
    for province, score in dict_scores.items():
        try:
            infection = dict_infect[province]
        except KeyError:
            logger.warning(f"Province {province} has no infected value. Skipped.")
            continue
        list_provinces.append(province)
        list_scores.append(score)
        list_infect.append(infection)

    # Scatter plot of NPI vs infection
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
    plt.ylabel("Infections per day (100,000 inhabitants)")
    plt.savefig(path_data / "npi_vs_infection.png")


if __name__ == "__main__":
    typer.run(main)
