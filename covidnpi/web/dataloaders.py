from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo


def return_ambits_by_province(
    province: str, ambits: tuple, path_config: str = "covidnpi/config.toml"
):
    """Loads the scores stored in mongo for a given combination of province and ambits

    Parameters
    ----------
    province : str
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

    x = col.find_one({"provincia": "fechas"})["x"]
    dict_provincia = col.find_one({"provincia": province})

    dict_plot = {}

    for ambit in ambits:
        try:
            y = dict_provincia[ambit]
        except KeyError:
            raise KeyError(f"Ambito '{ambit}' no existe")
        except TypeError:
            raise KeyError(f"Provincia '{province}' no encontrada")
        dict_plot.update({ambit: {"x": x, "y": y}})

    return dict_plot


def return_provinces_by_ambit(
    ambit: str, provinces: tuple, path_config: str = "covidnpi/config.toml"
):
    """Loads the scores stored in mongo for a given combination of provinces and ambit

    Parameters
    ----------
    ambit : str
    provinces : tuple
    path_config : str, optional

    Returns
    -------
    dict_plot : dict
        {province: {x, y}}
        x are dates in string format, y are the score values

    """
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    x = col.find_one({"provincia": "fechas"})["x"]

    dict_plot = {}

    for province in provinces:
        dict_provincia = col.find_one({"provincia": province})
        try:
            y = dict_provincia[ambit]
        except KeyError:
            raise KeyError(f"Ambito '{ambit}' no existe")
        except TypeError:
            raise KeyError(f"Provincia '{province}' no encontrada")
        dict_plot.update({province: {"x": x, "y": y}})

    return dict_plot


def return_casos_of_province(province: str, path_config: str = "covidnpi/config.toml"):
    """Loads the number of cases stored in mongo for a given province

    Parameters
    ----------
    province : str
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

    x = col.find_one({"provincia": province})
    dict_plot = {"x": x["fechas"], "y": x["casos"]}
    return dict_plot


def return_crecimiento_of_province(
    province: str, path_config: str = "covidnpi/config.toml"
):
    """Loads the growth of cases stored in mongo for a given province

    Parameters
    ----------
    province : str
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

    x = col.find_one({"provincia": province})
    dict_plot = {"x": x["fechas"], "y": x["crecimiento"]}
    return dict_plot
