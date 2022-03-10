import json
from pathlib import Path
from typing import Iterable


def list_ambitos(path_data: Path) -> Iterable[str]:
    """List the areas currently available, using the file
    'ambitos.json'

    Parameters
    ----------
    path_data : Path
        Path to data folder, containing 'ambitos.json' file

    Returns
    -------
    Iterable[str]
        List of areas
    """
    path_json = path_data / "ambitos.json"
    try:
        with open(path_json) as f:
            dict_areas = json.load(f)
            list_areas = [d["value"] for d in dict_areas]
    except FileNotFoundError as err:
        raise FileNotFoundError(
            f"{err}\n[IMPORTANT] Run `covidnpi/web/generate_json.py` first!"
        )
    return list_areas
