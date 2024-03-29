import numpy as np
import pandas as pd


def cumulative_cases(x: pd.Series, w: int) -> pd.Series:
    """Computes the cumulative cases of a series

    Parameters
    ----------
    x : pandas.Series
    w : int
        Size of the acumulation

    Returns
    -------
    pandas.Series

    """
    idx = x.index
    x_cum = np.convolve(x, np.ones(w), "valid")
    x_cum = pd.Series(x_cum, index=idx[(w - 1) :])
    return x_cum


def moving_average(x: pd.Series, w: int) -> pd.Series:
    """Computes the moving average of a series

    Parameters
    ----------
    x : pandas.Series
    w : int
        Size of the moving average

    Returns
    -------
    pandas.Series

    """
    x_movavg = cumulative_cases(x, w) / w
    return x_movavg


def compute_growth_rate(series: pd.Series, days: int) -> pd.Series:
    """Computes the growth of a series, comparing intervals of time

    Parameters
    ----------
    series : pandas.Series
    days : int
        Size of the intervals

    Returns
    -------
    pandas.Series
        Growth of the series per date (in percentage)
    """
    x = moving_average(series, days)
    idx = x.index
    # GR = ( IA7(t) - IA7(t-7) ) * 100 / IA7(t-7)
    g = np.divide(x.values, x.shift(days).values)
    # Replace infs with NaN
    g[g == np.inf] = np.nan
    g = pd.Series(g, index=idx)
    # Center around 0 and change to percentage
    g = (g - 1) * 100
    return g


def compute_logarithmic_growth_rate(series: pd.Series, days: int) -> pd.Series:
    """Computes the logarithmic growth of a series, comparing intervals of time

    Parameters
    ----------
    series : pandas.Series
    days : int
        Size of the intervals

    Returns
    -------
    pandas.Series
        Logarithmic growth of the series per date
    """
    x = moving_average(series, days)
    idx = x.index
    # LR = ln( 1 + GR / 100 ) = ln( IA7(t) / IA7(t - 7) )
    lr = np.log(np.divide(x.values, x.shift(days).values))
    # Replace infs with NaN
    lr[lr == np.inf] = np.nan
    lr[lr == -np.inf] = np.nan
    return pd.Series(lr, index=idx)
