from typing import Dict, List, Tuple

from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo


def slice_dates(x: List, cfg: Dict) -> Tuple:
    """Locate position of minimum and maximum dates

    Parameters
    ----------
    x : List
        List of dates, sorted
    cfg : Dict
        Config with keys "date_min" and "date_max"

    Returns
    -------
    Tuple
        Position of minimum and maximum dates
    """
    try:
        idx_min = x.index(cfg["date_min"])
    except ValueError:
        idx_min = 0
    try:
        idx_max = x.index(cfg["date_max"])
    except ValueError:
        idx_max = len(x)
    return idx_min, idx_max


def return_scores_of_fields_by_province(
    code: str, fields: tuple, path_config: str = "covidnpi/config.toml"
) -> Dict:
    """Loads the scores stored in mongo for a given combination of province and fields

    Parameters
    ----------
    code : str
    fields : tuple
    path_config : str, optional

    Returns
    -------
    dict_plot : dict
        {field: {x, y}}
        x are dates in string format, y are the score values

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    dict_provincia = col.find_one({"code": code})
    try:
        x = dict_provincia["dates"]
    except TypeError:
        print(f"[ERROR] No data for code '{code}', from collection 'cases'")
        return {
            field: {
                "x": [],
                "y": [],
                "y_max": 1,
                "y_min": 0,
                "x_max": cfg_mongo["date_max"],
                "x_min": cfg_mongo["date_min"],
            }
            for field in fields
        }

    dict_plot = {}
    idx_min, idx_max = slice_dates(x, cfg_mongo)
    x = x[idx_min:idx_max]

    for field in fields:
        try:
            y = dict_provincia[field][idx_min:idx_max]
        except KeyError:
            print(f"[ERROR] Field '{field}' not found for '{code}'")
            y = [0] * len(x)
        except TypeError:
            print(f"[ERROR] Province '{code}' not found")
            y = [0] * len(x)
        dict_field = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": cfg_mongo["date_max"],
            "x_min": cfg_mongo["date_min"],
        }
        dict_plot.update({field: dict_field})

    return dict_plot


def return_scores_of_provinces_by_field(
    field: str, codes: tuple, path_config: str = "covidnpi/config.toml"
) -> Dict:
    """Loads the scores stored in mongo for a given combination of provinces and field

    Parameters
    ----------
    field : str
    codes : tuple
    path_config : str, optional

    Returns
    -------
    dict_plot : dict
        {code: {x, y}}
        x are dates in string format, y are the score values

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    dict_plot = {}

    # Initialize x
    x = [cfg_mongo["date_min"]]

    for code in codes:
        dict_provincia = col.find_one({"code": code})
        try:
            x = dict_provincia["dates"]
            y = dict_provincia[field]
        except KeyError:
            print(f"[ERROR] Field '{field}' not found for '{code}'")
            y = [0] * len(x)
        except TypeError:
            print(f"[ERROR] Province '{code}' not found")
            y = [0] * len(x)
        idx_min, idx_max = slice_dates(x, cfg_mongo)
        x = x[idx_min:idx_max]
        y = y[idx_min:idx_max]
        dict_code = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": cfg_mongo["date_max"],
            "x_min": cfg_mongo["date_min"],
        }
        dict_plot.update({code: dict_code})

    return dict_plot


def return_cases_of_province(
    code: str, path_config: str = "covidnpi/config.toml"
) -> Dict:
    """Loads the number of cases stored in mongo for a given province

    Parameters
    ----------
    code : str
    path_config : str, optional

    Returns
    -------
    dict_plot : dict
        {x, y}
        x are dates in string format, y are the number of cases

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("cases")

    x = col.find_one({"code": code})
    try:
        dates = x["dates"]
        cases = x["cases"]
    except (KeyError, TypeError) as er:
        print(f"[ERROR] No data for code '{code}', from collection 'cases': {er}")
        dates = []
        cases = []

    idx_min, idx_max = slice_dates(dates, cfg_mongo)
    dates = dates[idx_min:idx_max]
    cases = cases[idx_min:idx_max]

    dict_plot = {
        "x": dates,
        "y": cases,
        "y_max": 800,
        "y_min": 0,
        "x_max": cfg_mongo["date_max"],
        "x_min": cfg_mongo["date_min"],
    }
    return dict_plot


def return_growth_of_province(
    code: str, path_config: str = "covidnpi/config.toml", logarithmic: bool = True
) -> Dict:
    """Loads the growth of cases stored in mongo for a given province

    Parameters
    ----------
    code : str
    path_config : str, optional
    logarithmic : bool, optional
        Return LR instead of GR, by default True

    Returns
    -------
    dict_plot : dict
        {x, y}
        x are dates in string format, y are the growth values

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("cases")

    x = col.find_one({"code": code})
    if logarithmic:
        key = "logarithmic_growth_rate"
        y_max = 1.2
        y_min = -1.2
    else:
        key = "growth_rate"
        y_max = 200
        y_min = -100
    try:
        dates = x["dates"]
        gr = x[key]
    except (KeyError, TypeError) as er:
        print(f"[ERROR] No data for code '{code}', from collection 'cases': {er}")
        dates = []
        gr = []

    idx_min, idx_max = slice_dates(dates, cfg_mongo)
    dates = dates[idx_min:idx_max]
    gr = gr[idx_min:idx_max]

    dict_plot = {
        "x": dates,
        "y": gr,
        "y_max": y_max,
        "y_min": y_min,
        "x_max": cfg_mongo["date_max"],
        "x_min": cfg_mongo["date_min"],
    }
    return dict_plot


def return_statistics_of_field_by_province(
    code: str, path_config: str = "covidnpi/config.toml"
) -> List[Dict]:
    """Loads the list of statistics by field, for a given province

    Parameters
    ----------
    code : str
        Province code
    path_config : str, optional
        Path to config, by default "covidnpi/config.toml"

    Returns
    -------
    List[Dict]
        List of dictionaries with format {"r": List[float], "theta": List[str], "name": str}
    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    x = col.find_one({"code": code})
    list_fields = x["fields"]
    list_fields.append(list_fields[0])
    list_statistics = col.find_one({"code": "statistics"})
    list_plot = []
    for key in list_statistics["list"]:
        try:
            r = x[key]
        except KeyError:
            continue
        r.append(r[0])
        list_plot.append(
            {"r": r, "theta": list_fields, "name": key, "type": x["types"][key]}
        )
    return list_plot


def return_scores_boxplot_of_field(
    code: str, path_config: str = "covidnpi/config.toml"
) -> List[Dict]:
    """Loads the list of boxplot for a given field of activity

    Parameters
    ----------
    code : str
        Field of activity code
    path_config : str, optional
        Path to config, by default "covidnpi/config.toml"

    Returns
    -------
    List[Dict]
        List of dictionaries with format {"x": List[str], "y": List[float], "color": str, "name": str}
    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    col = mongo.get_col("boxplot")
    x = col.find_one({"code": code})
    dict_color = col.find_one({"code": "color"})
    try:
        list_dates = x["dates"]
    except (KeyError, TypeError) as er:
        print(f"[ERROR] Code '{code}' not found in 'boxplot': {er}")
        return [
            {
                "x": [],
                "y": [],
                "color": "#FFFFFF",
                "name": "No data",
                "fill": "none",
                "y_max": 0,
                "y_min": 1,
                "x_max": cfg_mongo["date_max"],
                "x_min": cfg_mongo["date_min"],
            }
        ]

    # Define X limits
    idx_min, idx_max = slice_dates(list_dates, cfg_mongo)
    list_dates = list_dates[idx_min:idx_max]

    # Define Y limits
    if code == "gr":
        y_min, y_max = -100, 200
    elif code == "ci":
        y_min, y_max = 0, 800
    else:
        y_min, y_max = 0, 1

    list_out = []
    # Loop through boxplot lines
    for key, color in dict_color.items():
        # Skip unwanted keys
        if (key == "_id") or (key == "code"):
            continue
        try:
            list_out.append(
                {
                    "x": list_dates,
                    "y": x[key][idx_min:idx_max],
                    "color": color,
                    "name": key,
                    "fill": "tonexty",
                    "y_max": y_max,
                    "y_min": y_min,
                    "x_max": cfg_mongo["date_max"],
                    "x_min": cfg_mongo["date_min"],
                }
            )
        except KeyError:
            print(f"[ERROR] Key '{key}' not found in boxplot '{code}'. Skipped!")
    # Do not color last
    list_out[0].update({"fill": "none"})
    return list_out
