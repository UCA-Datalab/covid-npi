from pathlib import Path

import pandas as pd
import typer

from covidnpi.utils.cases import load_cases_df, return_cases_of_provincia_normed
from covidnpi.utils.config import load_config
from covidnpi.utils.series import (
    compute_growth_rate,
    compute_logarithmic_growth_rate,
    cumulative_cases,
    moving_average,
)


def main(path_output: str = "output", path_config: str = "config.toml"):
    """Compute and store the cases rates of each province in Spain

    Parameters
    ----------
    path_output : str, optional
        Folder where the results are stored, by default "output"
    path_config : str, optional
        Config file
    """
    # Load the raw cases rates
    cases = load_cases_df()
    # Change variable to Path type
    path_output = Path(path_output)
    # Get the size of the time window
    cfg_cases = load_config(path_config, key="cases")
    days = cfg_cases["movavg"]

    # Initialize the dictionaries
    dict_daily = {}
    dict_acum = {}
    dict_growth = {}
    dict_lr = {}
    dict_mean = {}

    # Loop through each province
    for provincia in cases["provincia_iso"].dropna().unique():
        # Compute daily cases
        try:
            ser = return_cases_of_provincia_normed(cases, provincia)
        except KeyError:
            print(f"-----\nProvincia {provincia} missing from poblacion\n-----")
            continue
        dict_daily.update({provincia: ser})
        # Compute acumulated cases
        ser_acum = cumulative_cases(ser, days).fillna(0)
        dict_acum.update({provincia: ser_acum})
        # Compute the growth rate of cases
        ser_growth = compute_growth_rate(ser, days).fillna(0)
        dict_growth.update({provincia: ser_growth})
        # Compute the logarithmic growth rate of cases
        ser_lr = compute_logarithmic_growth_rate(ser, days).fillna(0)
        dict_lr.update({provincia: ser_lr})
        # Compute the mean cases
        ser_mean = moving_average(ser, days).fillna(0)
        dict_mean.update({provincia: ser_mean})

    # Store all cases rates
    pd.DataFrame(dict_daily).to_csv(path_output / "covid_cases_daily.csv")
    pd.DataFrame(dict_acum).to_csv(path_output / f"covid_cases_cumulative_{days}.csv")
    pd.DataFrame(dict_growth).to_csv(path_output / f"covid_growth_rate_{days}.csv")
    pd.DataFrame(dict_lr).to_csv(path_output / f"covid_growth_rate_log_{days}.csv")
    pd.DataFrame(dict_mean).to_csv(path_output / f"covid_cases_average_{days}.csv")


if __name__ == "__main__":
    typer.run(main)
