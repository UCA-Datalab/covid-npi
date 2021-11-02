import datetime as dt
from pathlib import Path
from typing import Dict

import pandas as pd
import typer
from covidnpi.utils.ambitos import list_ambitos
from scipy.integrate import trapz


def dataframe_of_scores_mean_by_ambito(path_data: Path) -> pd.DataFrame:
    """Returns a dataframe with the mean NPI score per province (columns)
    and date (rows).

    Parameters
    ----------
    path_data : Path
        Path to the data folder. Must contain the folder "score_ambito"

    Returns
    -------
    pd.DataFrame
        Dataframe with mean NPI scores
    """
    # Path to score_ambito
    path_area = path_data / "score_ambito"
    # List the ambitos of interest
    list_amb = list_ambitos(path_data)
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
        # Compute the area under the curve and store
        dict_ambito.update({province: ser})
    return pd.DataFrame.from_dict(dict_ambito)


def compute_area_of_dataframe_columns(df: pd.DataFrame) -> Dict:
    """Retuns a dictionary with the area under the series of each
    column in the dataframe. Keys are the name of the columns.

    Parameters
    ----------
    df : pd.DataFrame
        Pandas dataframe, containing numeric values.

    Returns
    -------
    Dict
        Column: Area
    """
    dict_areas = {}
    for column in df:
        ser = df[column]
        dict_areas.update({column: trapz(ser)})
    return dict_areas


def dict_of_scores_area_by_ambito(
    path_data: Path,
    date_min: dt.datetime = dt.datetime(2020, 9, 15),
    date_max: dt.datetime = dt.datetime(2021, 5, 8),
) -> Dict:
    """Returns a dictionary that contains the NPI area score
    of each province.

    Parameters
    ----------
    path_data : Path
        Path to the data folder. Must contain the folder "score_ambito"
    date_min : dt.datetime, optional
        Minimum date, by default dt.datetime(2020, 9, 15)
    date_max : dt.datetime, optional
        [Maximum date, by default dt.datetime(2021, 5, 8)

    Returns
    -------
    Dict
        Province: NPI score area
    """
    df = dataframe_of_scores_mean_by_ambito(path_data)
    # Limit dataframe within date range
    df = df[(df.index >= date_min) & (df.index <= date_max)]
    return compute_area_of_dataframe_columns(df)


def main(path_data: str = "output"):
    path_data = Path(path_data)
    dict_scores = dict_of_scores_area_by_ambito(path_data)
    print(dict_scores)


if __name__ == "__main__":
    typer.run(main)
