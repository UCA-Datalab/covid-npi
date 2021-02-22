import json

import typer

from covidnpi.utils.config import load_config
from covidnpi.utils.preprocess import clean_pandas_str
from covidnpi.utils.taxonomia import return_taxonomia


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


def json_ambitos(path_taxonomia: str, path_json: str):
    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia)
    ambitos_raw = taxonomia["ambito"].drop_duplicates().reset_index()
    ambitos_clean = clean_pandas_str(ambitos_raw)

    list_json = []
    for i, raw in ambitos_raw.iteritems():
        list_json.append({"value": ambitos_clean[i], "text": raw})

    with open(path_json, "w") as outfile:
        json.dump(list_json, outfile)


def main(
    path_taxonomia: str = "datos_NPI/Taxonomía_07022021.xlsx",
    path_config: str = "covidnpi/config.toml",
    path_json_provincia: str = "provincias.json",
    path_json_medidas: str = "medidas.json",
):
    code_to_provincia = load_config(path_config, key="code_to_provincia")
    json_code_to_provincia(code_to_provincia, path_json=path_json_provincia)
    json_ambitos(path_taxonomia, path_json_medidas)


if __name__ == "__main__":
    typer.run(main)
