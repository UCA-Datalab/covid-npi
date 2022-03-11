import os

import typer

from covidnpi.score.fields import return_dict_fields
from covidnpi.score.islas import return_dict_islas
from covidnpi.score.items import return_dict_items
from covidnpi.score.medidas import return_dict_medidas
from covidnpi.utils.dictionaries import (
    store_dict_provincia_to_medidas,
    store_dict_scores,
    update_keep_old_keys,
)
from covidnpi.utils.log import logger
from covidnpi.utils.mobility import mobility_report_to_csv
from covidnpi.utils.preprocess import read_npi_and_build_dict
from covidnpi.utils.taxonomy import PATH_TAXONOMY


def main(
    path_raw: str = "datos_NPI",
    path_taxonomy: str = PATH_TAXONOMY,
    path_output: str = "output",
):
    """Reads the raw data stored in `path_raw`, preprocess and scores it, while storing
    all the results in `path_output`. An additional path to the taxonomy xlsx file
    must also be provided in `path_taxonomy`.

    Parameters
    ----------
    path_raw : str, optional
        Path to raw data, by default "datos_NPI_2"
    path_taxonomy : str, optional
        Path to taxonomy xlsx file, by default `PATH_TAXONOMY`
    path_output : str, optional
        Output folder, by default "output"

    """
    logger.debug(f"Reading raw data from {path_raw}")
    dict_medidas = read_npi_and_build_dict(
        path_data=path_raw, path_taxonomy=path_taxonomy
    )

    # Build output path
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    path_medidas = os.path.join(path_output, "medidas")
    store_dict_provincia_to_medidas(dict_medidas, path_output=path_medidas)
    logger.debug(
        f"The processed interventions have been stored in {path_medidas}\n\n...\n\n"
        f"Next step is to score each intervention."
    )

    dict_scores = return_dict_medidas(dict_medidas)
    path_medidas = os.path.join(path_output, "medidas")
    store_dict_scores(dict_scores, path_output=path_medidas)
    logger.debug(
        "The score of each intervention per province has been stored in "
        f"{path_medidas}\n\n...\n\nNext step is to score the items."
    )

    dict_items = return_dict_items(dict_scores)
    path_items = os.path.join(path_output, "items")
    store_dict_scores(dict_items, path_output=path_items)
    logger.debug(
        "The score of each item per province has been stored in "
        f"{path_items}\n\n...\n\nNext step is to score the fields of activity."
    )

    dict_field = return_dict_fields(dict_items, path_taxonomy=path_taxonomy)
    dict_islas = return_dict_islas(dict_field)
    dict_field = update_keep_old_keys(dict_field, dict_islas)
    path_score_field = os.path.join(path_output, "score_field")
    store_dict_scores(dict_field, path_output=path_score_field)

    logger.debug(
        "The score of each field per province has been stored in "
        f"{path_score_field}\n\n...\n\nNext step is to compute the mobility data."
    )

    path_mobility = os.path.join(path_output, "mobility")
    mobility_report_to_csv(path_output=path_mobility)
    logger.debug(f"Mobility data has been stored in {path_mobility}\n")


if __name__ == "__main__":
    typer.run(main)
