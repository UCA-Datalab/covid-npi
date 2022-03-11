from typing import Dict

from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo

DATE_MIN = "2020-07-01"


def return_fields_by_province(
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
    x = dict_provincia["fechas"]

    dict_plot = {}

    for field in fields:
        try:
            y = dict_provincia[field]
        except KeyError:
            print(f"[ERROR] Ambito '{field}' no existe para '{code}'")
            y = [0] * len(x)
        except TypeError:
            print(f"[ERROR] Provincia '{code}' no encontrada")
            y = [0] * len(x)
        dict_field = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": x[-1],
            "x_min": DATE_MIN,
        }
        dict_plot.update({field: dict_field})

    return dict_plot


def return_provinces_by_field(
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
    x = [DATE_MIN]

    for code in codes:
        dict_provincia = col.find_one({"code": code})
        try:
            x = dict_provincia["fechas"]
            y = dict_provincia[field]
        except KeyError:
            print(f"[ERROR] Ambito '{field}' no existe para '{code}'")
            y = [0] * len(x)
        except TypeError:
            print(f"[ERROR] Provincia '{code}' no encontrada")
            y = [0] * len(x)
        dict_code = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": x[-1],
            "x_min": DATE_MIN,
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
        x_max = x["fechas"][-1]
    except KeyError:
        print(f"[ERROR] El codigo '{code}' de 'cases' no tiene 'x'")
        x_max = DATE_MIN

    dict_plot = {
        "x": x["fechas"],
        "y": x["cases"],
        "y_max": 800,
        "y_min": 0,
        "x_max": x_max,
        "x_min": DATE_MIN,
    }
    return dict_plot


def return_growth_of_province(
    code: str, path_config: str = "covidnpi/config.toml"
) -> Dict:
    """Loads the growth of cases stored in mongo for a given province

    Parameters
    ----------
    code : str
    path_config : str, optional

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
    try:
        x_max = x["fechas"][-1]
    except KeyError:
        print(f"[ERROR] El codigo '{code}' de 'cases' no tiene 'x'")
        x_max = DATE_MIN
    dict_plot = {
        "x": x["fechas"],
        "y": x["crecimiento"],
        "y_max": 200,
        "y_min": -100,
        "x_max": x_max,
        "x_min": DATE_MIN,
    }
    return dict_plot
