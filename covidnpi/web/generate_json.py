import json

import typer

from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo


def json_code_to_provincia(code_to_provincia: dict, path_json: str):
    """Stores the dictionary code_to_provincia in json format with the style:
    [{value: M, text: Madrid}, ...]

    Parameters
    ----------
    code_to_provincia : dict
        {M: Madrid}
    path_json : str
        Path where the json is stored, must end in a file with json format

    """
    list_json = []
    for value, text in code_to_provincia.items():
        list_json.append({"value": value, "text": text})

    with open(path_json, "w") as outfile:
        json.dump(list_json, outfile, ensure_ascii=False)


def json_ambitos(path_config: str, path_json: str):
    """Stores the ambits in json format with the style:
    [{value: deporte_exterior, text: Deporte exterior}, ...]

    Parameters
    ----------
    path_config : str
        Path to config toml file
    path_json : str
        Path where the json is stored, must end in a file with json format

    """
    cfg_mongo = load_config(path_config, "mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")
    dict_provincia = col.find_one({"code": "M"})
    list_ambitos = [k for k in dict_provincia.keys()]
    for remove in ["code", "provincia", "fechas", "_id"]:
        list_ambitos.remove(remove)

    list_json = []
    for value in list_ambitos:
        text = value.replace("_", " ").capitalize()
        list_json.append({"value": value, "text": text})

    with open(path_json, "w") as outfile:
        json.dump(list_json, outfile, ensure_ascii=False)


def generate_json(
    path_config: str = "covidnpi/config.toml",
    path_json_provincia: str = "output/provincias.json",
    path_json_ambitos: str = "output/ambitos.json",
):
    """Generates and stores both provinces and ambits json

    Parameters
    ----------
    path_config : str, optional
        Path to the config toml file
    path_json_provincia : str, optional
        Path where the provinces json is stored, must end in a file with json format
    path_json_ambitos : str, optional
        Path where the ambits json is stored, must end in a file with json format

    """
    print(f"\n-----\nStoring provinces json in {path_json_provincia}\n-----")
    code_to_provincia = load_config(path_config, key="code_to_provincia")
    json_code_to_provincia(code_to_provincia, path_json=path_json_provincia)
    print(f"\n-----\nStoring ambits json in {path_json_ambitos}\n-----")
    json_ambitos(path_config, path_json_ambitos)


if __name__ == "__main__":
    typer.run(generate_json)
