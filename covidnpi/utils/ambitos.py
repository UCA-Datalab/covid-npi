import json
from pathlib import Path
from typing import Iterable


def list_ambitos(path_data: Path) -> Iterable[str]:
    """List the areas currently available

    Parameters
    ----------
    path_data : Path
        Path to data folder

    Returns
    -------
    Iterable[str]
        List of areas
    """
    path_json = path_data / "ambitos.json"
    with open(path_json) as f:
        dict_areas = json.load(f)
        list_areas = [d["value"] for d in dict_areas]
    return list_areas
