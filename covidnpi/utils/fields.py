import json
from pathlib import Path
from typing import Iterable


def list_fields(path_data: Path) -> Iterable[str]:
    """List the fields currently available, using the file
    'fields.json'

    Parameters
    ----------
    path_data : Path
        Path to data folder, containing 'fields.json' file

    Returns
    -------
    Iterable[str]
        List of fields
    """
    path_json = path_data / "fields.json"
    try:
        with open(path_json) as f:
            dict_fields = json.load(f)
            list_fields = [d["value"] for d in dict_fields]
    except FileNotFoundError as err:
        raise FileNotFoundError(
            f"{err}\n[IMPORTANT] Run `covidnpi/initialize_web.py` first!"
        )
    return list_fields
