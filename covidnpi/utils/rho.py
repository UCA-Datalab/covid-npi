import numpy as np
import pandas as pd

from covidnpi.utils.series import moving_average


def compute_cases_weighted(series_cases: pd.Series, days: int = 7) -> pd.Series:
    """Computes weighted cases: cases per day divided by the average cases
    during the last days

    Parameters
    ----------
    series_cases : pandas.Series
        COVID cases per date
    days : int, optional
        Size of the cumulative sum, by default 7

    Returns
    -------
    pandas.Series
        COVID cases per date, normalized by the average cases of the last days

    """
    acum = moving_average(series_cases, days)
    series_cases_peso = np.divide(series_cases, acum)
    return series_cases_peso


def compute_cases_normed(
    series_cases: pd.Series, days: int = 7, num_lag: int = 4
) -> pd.Series:
    """

    Parameters
    ----------
    series_cases : pandas.Series
        COVID cases per date
    days : int, optional
        Size of the cumulative sum, by default 7
    num_lag : int, optional
        Number of lags to use, by default 4

    Returns
    -------
    pandas.Series

    """
    series_cases_peso = compute_cases_weighted(series_cases, days=days)
    list_series_peso = [
        series_cases_peso.shift(lag * days) for lag in range(num_lag + 1)
    ]
    series_mean = pd.concat(list_series_peso, axis=1).mean(axis=1)
    series_cases_norm = np.divide(series_cases, series_mean)
    return series_cases_norm


def compute_rho(
    series_cases: pd.Series, days: int = 7, lag_peso: int = 4, lag_norm: int = 6
) -> pd.Series:
    """

    Parameters
    ----------
    series_cases : pandas.Series
        COVID cases per date
    days : int, optional
        Size of the cumulative sum, by default 7
    lag_peso : int, optional
        Number of lags to use when computing weighted cases, by default 4
    lag_norm : int, optional
        Number of lags to use when computing movavg normed cases, by default 7

    Returns
    -------
    pandas.Series
        Rho

    """
    # Compute the moving average of normed cases
    series_cases_norm = compute_cases_normed(series_cases, days=days, num_lag=lag_peso)
    series_norm_movavg = moving_average(series_cases_norm, lag_norm)
    # Compute rho
    list_numerator = [series_norm_movavg.shift(lag) for lag in range(3)]
    numerator = pd.concat(list_numerator, axis=1).mean(axis=1)
    list_denominator = [series_norm_movavg.shift(lag) for lag in range(5, 8)]
    denominator = pd.concat(list_denominator, axis=1).mean(axis=1)
    return np.divide(numerator, denominator)
