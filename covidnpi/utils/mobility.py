import pandas as pd

URL_MOBILITY = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"


def load_mobility_report(
    country: str = "ES", path_csv: str = URL_MOBILITY
) -> pd.DataFrame:
    """Loads the Google mobility report of a certain country. Adds additional columns:
    - code : province code

    Parameters
    ----------
    country : str, optional
        Code of the country to load, by default "ES"
    path_csv : str, optional
        Link or path to the mobility report csv

    Returns
    -------
    pandas.DataFrame
        Mobility report of given country

    """
    # Process in chunks to not saturate the memory
    df_list = []
    for chunk in pd.read_csv(
        path_csv, parse_dates=["date"], dayfirst=False, chunksize=5e5, low_memory=False
    ):
        df_list += [chunk.query(f"country_region_code == '{country}'")]
    mob = pd.concat(df_list)
    del df_list

    # Codes of each province
    mob["code"] = mob["iso_3166_2_code"].str.replace(f"{country}-", "")
    return mob


def return_reports_of_provincia(mob: pd.DataFrame, code: str) -> dict:
    """Returns a dictionary containing all the reports for a given province

    Parameters
    ----------
    mob : pandas.DataFrame
        Mobility report dataframe
    code : str
        Province code

    Returns
    -------
    dict
        Contains pandas.Series

    """
    df = mob.query(f"code == '{code}'").set_index("date")
    list_reports = [col for col in mob.columns if "percent" in col]
    dict_reports = {}
    for col in list_reports:
        name = col.split("_", 1)[0]
        series = df[col]
        dict_reports.update({name: series})
    return dict_reports
