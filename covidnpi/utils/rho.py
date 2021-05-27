import numpy as np
import pandas as pd

from covidnpi.utils.series import moving_average


def compute_incidence_weighted(series_casos: pd.Series, days: int = 7) -> pd.Series:
    """Computes weighted incidence: incidence per day divided by the average incidence
    during the last days

    Parameters
    ----------
    series_casos : pandas.Series
        COVID incidence per date
    days : int, optional
        Size of the cumulative sum, by default 7

    Returns
    -------
    pandas.Series
        COVID incidence per date, normalized by the average incidence of the last days

    """
    acum = moving_average(series_casos, days)
    series_casos_peso = np.divide(series_casos, acum)
    return series_casos_peso


def compute_incidence_normed(
    series_casos: pd.Series, days: int = 7, num_lag: int = 4
) -> pd.Series:
    """

    Parameters
    ----------
    series_casos : pandas.Series
        COVID incidence per date
    days : int, optional
        Size of the cumulative sum, by default 7
    num_lag : int, optional
        Number of lags to use, by default 4

    Returns
    -------
    pandas.Series

    """
    series_casos_peso = compute_incidence_weighted(series_casos, days=days)
    list_series_peso = [
        series_casos_peso.shift(lag * days) for lag in range(num_lag + 1)
    ]
    series_mean = pd.concat(list_series_peso, axis=1).mean(axis=1)
    series_casos_norm = np.divide(series_casos, series_mean)
    return series_casos_norm


def compute_rho(
    series_casos: pd.Series, days: int = 7, lag_peso: int = 4, lag_norm: int = 6
) -> pd.Series:
    """

    Parameters
    ----------
    series_casos : pandas.Series
        COVID incidence per date
    days : int, optional
        Size of the cumulative sum, by default 7
    lag_peso : int, optional
        Number of lags to use when computing weighted incidence, by default 4
    lag_norm : int, optional
        Number of lags to use when computing movavg normed incidence, by default 7

    Returns
    -------
    pandas.Series
        Rho

    """
    # Compute the moving average of normed incidence
    series_casos_norm = compute_incidence_normed(
        series_casos, days=days, num_lag=lag_peso
    )
    series_norm_movavg = moving_average(series_casos_norm, lag_norm)
    # Compute rho
    list_numerator = [series_norm_movavg.shift(lag) for lag in range(3)]
    numerator = pd.concat(list_numerator, axis=1).mean(axis=1)
    list_denominator = [series_norm_movavg.shift(lag) for lag in range(5, 8)]
    denominator = pd.concat(list_denominator, axis=1).mean(axis=1)
    return np.divide(numerator, denominator)
