from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo
from covidnpi.utils.log import logger

DATE_MIN = "2020-07-01"


def return_ambits_by_province(
    code: str, ambits: tuple, path_config: str = "covidnpi/config.toml"
):
    """Loads the scores stored in mongo for a given combination of province and ambits

    Parameters
    ----------
    code : str
    ambits : tuple
    path_config : str, optional

    Returns
    -------
    dict_plot : dict
        {ambit: {x, y}}
        x are dates in string format, y are the score values

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    dict_provincia = col.find_one({"code": code})
    x = dict_provincia["fechas"]

    dict_plot = {}

    for ambit in ambits:
        try:
            y = dict_provincia[ambit]
        except KeyError:
            logger.error(f"Ambito '{ambit}' no existe")
            y = [0] * len(x)
        except TypeError:
            logger.error(f"Provincia '{code}' no encontrada")
            y = [0] * len(x)
        dict_ambit = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": x[-1],
            "X_min": DATE_MIN,
        }
        dict_plot.update({ambit: dict_ambit})

    return dict_plot


def return_provinces_by_ambit(
    ambit: str, codes: tuple, path_config: str = "covidnpi/config.toml"
):
    """Loads the scores stored in mongo for a given combination of provinces and ambit

    Parameters
    ----------
    ambit : str
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

    for code in codes:
        dict_provincia = col.find_one({"code": code})
        x = dict_provincia["fechas"]
        try:
            y = dict_provincia[ambit]
        except KeyError:
            logger.error(f"Ambito '{ambit}' no existe")
            y = [0] * len(x)
        except TypeError:
            logger.error(f"Provincia '{code}' no encontrada")
            y = [0] * len(x)
        dict_code = {
            "x": x,
            "y": y,
            "y_max": 1,
            "y_min": 0,
            "x_max": x[-1],
            "X_min": DATE_MIN,
        }
        dict_plot.update({code: dict_code})

    return dict_plot


def return_incidence_of_province(code: str, path_config: str = "covidnpi/config.toml"):
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
    col = mongo.get_col("casos")

    x = col.find_one({"code": code})
    dict_plot = {
        "x": x["fechas"],
        "y": x["casos"],
        "y_max": 800,
        "y_min": 0,
        "x_max": x[-1],
        "X_min": DATE_MIN,
    }
    return dict_plot


def return_growth_of_province(code: str, path_config: str = "covidnpi/config.toml"):
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
    col = mongo.get_col("casos")

    x = col.find_one({"code": code})
    dict_plot = {
        "x": x["fechas"],
        "y": x["crecimiento"],
        "y_max": 200,
        "y_min": -100,
        "x_max": x[-1],
        "X_min": DATE_MIN,
    }
    return dict_plot
