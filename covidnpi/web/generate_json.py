import json

import typer

from covidnpi.utils.config import load_config
from covidnpi.utils.log import logger
from covidnpi.web.mongo import load_mongo
from covidnpi.utils.regions import ISOPROV_TO_PROVINCIA


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


def json_fields(path_config: str, path_json: str):
    """Stores the fields in json format with the style:
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
    list_fields = [k for k in dict_provincia.keys()]
    for remove in ["code", "province", "dates", "_id"]:
        try:
            list_fields.remove(remove)
        except ValueError:
            logger.warning(
                f"Could not remove key '{remove}' from list: {', '.join(list_fields)}"
            )

    list_json = []
    for value in list_fields:
        text = value.replace("_", " ").capitalize()
        list_json.append({"value": value, "text": text})

    with open(path_json, "w") as outfile:
        json.dump(list_json, outfile, ensure_ascii=False)


def generate_json(
    path_config: str = "covidnpi/config.toml",
    path_json_provincia: str = "output/provinces.json",
    path_json_fields: str = "output/fields.json",
):
    """Generates and stores both provinces and fields json

    Parameters
    ----------
    path_config : str, optional
        Path to the config toml file
    path_json_provincia : str, optional
        Path where the provinces json is stored, must end in a file with json format
    path_json_fields : str, optional
        Path where the fields json is stored, must end in a file with json format

    """
    logger.debug(f"\n-----\nStoring provinces json in {path_json_provincia}\n-----")
    json_code_to_provincia(ISOPROV_TO_PROVINCIA, path_json=path_json_provincia)
    logger.debug(f"\n-----\nStoring fields json in {path_json_fields}\n-----")
    json_fields(path_config, path_json_fields)


if __name__ == "__main__":
    typer.run(generate_json)
