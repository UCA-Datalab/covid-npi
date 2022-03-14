import matplotlib.pyplot as plt
import pandas as pd


def plot_categorical_distribution(
    df: pd.DataFrame,
    col: str,
    title: str = None,
    dict_names: dict = {},
    sort_index: bool = False,
    top: int = 100,
    figsize=(10, 5),
):
    """Plot the number of instances of each category, in bar format"""
    df_sub = df[col].dropna().value_counts().iloc[:top]
    df_sub.index = [dict_names.get(s, s) for s in df_sub.index]
    if sort_index:
        df_sub = df_sub.sort_index()
    df_sub.plot(kind="bar", zorder=3, figsize=figsize)
    plt.grid(zorder=0)
    plt.xlabel(col)
    if title is None:
        title = col
    plt.title(title)
    plt.show()
    plt.close()


def plot_date_distribution(
    df: pd.DataFrame, col: str, title: str = None, figsize: tuple = (10, 5)
):
    """Plots the number of instances per day to current plot"""
    plt.figure(figsize=figsize)
    df = df.copy()
    df_sub = df[col].dropna().value_counts().sort_index()
    plt.plot(df_sub, ".--", zorder=3)
    plt.grid(zorder=0)
    plt.xlabel("Fecha")
    if title is None:
        title = col
    plt.title(title)
    plt.show()
    plt.close()


def plot_continuous_distribution(
    df: pd.DataFrame,
    col: str,
    title: str = None,
    bins: int = 20,
    figsize: tuple = (10, 5),
    xlim=None,
):
    df[col].plot.hist(bins=bins, figsize=figsize, zorder=3, range=xlim)
    plt.grid(zorder=0)
    if title is None:
        title = col
    plt.title(title)
    plt.ylabel("Frecuencia")
    plt.show()
    plt.close()


def plot_categorical_distribution_by_date(
    df: pd.DataFrame,
    col: str,
    col_date: str,
    title: str = "",
    dict_names: dict = {},
    figsize: tuple = (10, 5),
    color_dict: dict = None,
):
    """Plot the number of instances per month and category, in bar format"""
    df_sub = df[[col, col_date]].dropna()
    if color_dict is not None:
        color = [color_dict.get(x, "red") for x in sorted(df_sub[col].unique())]
    else:
        color = None
    df_sub = (
        df_sub.groupby([df_sub[col_date].dt.year, df_sub[col_date].dt.month, col])
        .size()
        .unstack()
        .rename(dict_names, axis=1)
    )
    df_sub.plot(kind="bar", stacked=True, color=color, figsize=figsize, zorder=3)
    plt.grid(zorder=0)
    plt.xlabel("Fecha")
    plt.title(title)
    plt.show()
    plt.close()


def plot_date_difference(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    bins: int = 20,
    title: str = None,
    figsize: tuple = (10, 5),
    xlim=None,
):
    df = df.copy()
    df["NewCol"] = (df[col2] - df[col1]).dt.days
    if title is None:
        title = f"Días desde {col1} hasta {col2}"
    plot_continuous_distribution(
        df, "NewCol", bins=bins, title=title, figsize=figsize, xlim=xlim
    )


def compare_df_dates(
    df1, df2, col, label1="", label2="", title=None, xlim=None, figsize=(16, 5)
):
    """Compare two dataframes using the same date column"""
    plt.figure(figsize=figsize)
    df1_sub = df1[col].dropna().value_counts().sort_index()
    df2_sub = df2[col].dropna().value_counts().sort_index()
    plt.plot(df1_sub, ".--", zorder=3, label=label1)
    plt.plot(df2_sub, ".--", zorder=3, label=label2)
    plt.grid(zorder=0)
    plt.xlabel("Fecha")
    if title is None:
        title = col
    plt.title(title)
    if xlim is not None:
        plt.xlim(xlim)
    plt.legend()
    plt.show()
    plt.close()
