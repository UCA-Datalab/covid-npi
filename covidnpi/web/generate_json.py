import json

import typer

from covidnpi.utils.config import load_config


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
        json.dump(list_json, outfile)


def main(
    path_config: str = "covidnpi/config.toml",
    path_json_provincia: str = "provincias.json",
    path_json_medidas: str = "medidas.json",
):
    code_to_provincia = load_config(path_config, key="code_to_provincia")
    json_code_to_provincia(code_to_provincia, path_json=path_json_provincia)


if __name__ == "__main__":
    typer.run(main)
