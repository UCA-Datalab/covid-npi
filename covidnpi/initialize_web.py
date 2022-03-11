import typer

from covidnpi.utils.taxonomia import PATH_TAXONOMY
from covidnpi.web.datastore import datastore
from covidnpi.web.generate_json import generate_json


def main(
    path_output: str = "output",
    path_taxonomia=PATH_TAXONOMY,
    path_config: str = "config.toml",
    path_json_provincia: str = "output/provincias.json",
    path_json_ambitos: str = "output/ambitos.json",
):
    """Runs all the process needed to initalize the web:
    - Store the data in mongo
    - Generate the json files listing both the provinces and ambits

    Parameters
    ----------
    path_output : str, optional
        Path where the output of the preprocess_and_score script is located
    path_taxonomia : str, optional
        Path to taxonomia xlsx file
    path_config : str, optional
        Path to the config toml file
    path_json_provincia : str, optional
        Path where the provinces json is stored, must end in a file with json format
    path_json_ambitos : str, optional
        Path where the ambits json is stored, must end in a file with json format

    """
    datastore(
        path_output=path_output, path_taxonomia=path_taxonomia, path_config=path_config
    )
    generate_json(
        path_config=path_config,
        path_json_ambitos=path_json_ambitos,
        path_json_provincia=path_json_provincia,
    )


if __name__ == "__main__":
    typer.run(main)
