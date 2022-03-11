from pathlib import Path

import pandas as pd
import typer

from covidnpi.utils.casos import load_casos_df, return_casos_of_provincia_normed
from covidnpi.utils.series import (
    compute_growth_rate,
    cumulative_incidence,
    moving_average,
)


def main(days: int = 7, path_output: str = "output"):
    """Compute and store the incidence rates of each province in Spain

    Parameters
    ----------
    days : int, optional
        Number of days to apply the time window, by default 7
    path_output : str, optional
        Folder where the results are stored, by default "output"
    """
    casos = load_casos_df()
    path_output = Path(path_output)

    # Initialize the dictionaries
    dict_daily = {}
    dict_acum = {}
    dict_growth = {}
    dict_mean = {}

    # Loop through each province
    for provincia in casos["provincia_iso"].dropna().unique():
        # Compute daily incidence
        try:
            ser = return_casos_of_provincia_normed(casos, provincia)
        except KeyError:
            print(f"-----\nProvincia {provincia} missing from poblacion\n-----")
            continue
        dict_daily.update({provincia: ser})
        # Compute acumulated incidence
        ser_acum = cumulative_incidence(ser, days).fillna(0)
        dict_acum.update({provincia: ser_acum})
        # Compute the growth rate of incidence
        ser_growth = compute_growth_rate(ser, days).fillna(0)
        dict_growth.update({provincia: ser_growth})
        # Compute the mean incidence
        ser_mean = moving_average(ser, days).fillna(0)
        dict_mean.update({provincia: ser_mean})

    # Store all incidence rates
    pd.DataFrame(dict_daily).to_csv(path_output / "incidencia_diaria.csv")
    pd.DataFrame(dict_acum).to_csv(path_output / f"incidencia_acumulada_{days}.csv")
    pd.DataFrame(dict_growth).to_csv(path_output / f"incidencia_crecimiento_{days}.csv")
    pd.DataFrame(dict_mean).to_csv(path_output / f"incidencia_media_{days}.csv")


if __name__ == "__main__":
    typer.run(main)
