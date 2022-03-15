import typer

from covidnpi.utils.taxonomy import PATH_TAXONOMY
from covidnpi.web.datastore import datastore
from covidnpi.web.generate_json import generate_json


def main(
    path_output: str = "output",
    path_taxonomy: str = PATH_TAXONOMY,
    path_config: str = "config.toml",
    path_json_provincia: str = "output/provincias.json",
    path_json_fields: str = "output/fields.json",
    free_memory: bool = False,
):
    """Runs all the process needed to initalize the web:
    - Store the data in mongo
    - Generate the json files listing both the provinces and fields

    Parameters
    ----------
    path_output : str, optional
        Path where the output of the preprocess_and_score script is located
    path_taxonomy : str, optional
        Path to taxonomy xlsx file
    path_config : str, optional
        Path to the config toml file
    path_json_provincia : str, optional
        Path where the provinces json is stored, must end in a file with json format
    path_json_fields : str, optional
        Path where the fields json is stored, must end in a file with json format
    free_memory : bool, optional
        If True, free the memory of the database before loading new data, by default False

    """
    datastore(
        path_output=path_output,
        path_taxonomy=path_taxonomy,
        path_config=path_config,
        free_memory=free_memory,
    )
    generate_json(
        path_config=path_config,
        path_json_fields=path_json_fields,
        path_json_provincia=path_json_provincia,
    )


if __name__ == "__main__":
    typer.run(main)
