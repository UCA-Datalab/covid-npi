import numpy as np
import pandas as pd
from covidnpi.utils.series import cumulative_incidence


def compute_weight(casos: pd.Series, days: int = 7) -> pd.Series:
    acum = cumulative_incidence(casos, days)
    weight = days * np.divide(casos, acum)
    return weight


def compute_normed_incidence(
    casos: pd.Series, days: int = 7, num_lag: int = 4
) -> pd.Series:
    weight = compute_weight(casos, days=days)
    series_sum = weight
    for lag in range(1, num_lag + 1):
        series_sum += weight.shift(lag * days)
    casos_norm = (num_lag + 1) * np.divide(casos, series_sum)
    return casos_norm
