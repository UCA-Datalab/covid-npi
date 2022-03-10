import os

import typer

from covidnpi.score.ambitos import return_dict_ambitos
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
from covidnpi.utils.taxonomia import PATH_TAXONOMY


def main(
    path_raw: str = "datos_NPI",
    path_taxonomia: str = PATH_TAXONOMY,
    path_output: str = "output",
):
    """Reads the raw data stored in path_raw, preprocess and scores it, while storing
    all the results in path_output. An additional path to the taxonomia xlsx file
    must also be provided in path_taxonomia.

    Parameters
    ----------
    path_raw : str, optional
        Path to raw data, by default "datos_NPI_2"
    path_taxonomia : str, optional
        Path to taxonomia xlsx file, by default `PATH_TAXONOMY`
    path_output : str, optional
        Output folder, by default "output"

    """
    logger.debug(f"Leyendo datos crudos de {path_raw}")
    dict_medidas = read_npi_and_build_dict(
        path_data=path_raw, path_taxonomia=path_taxonomia
    )

    # Build output path
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    path_medidas = os.path.join(path_output, "medidas")
    store_dict_provincia_to_medidas(dict_medidas, path_output=path_medidas)
    logger.debug(
        f"Las medidas preprocesadas han sido guardadas en {path_medidas}\n\n...\n\n"
        f"Ahora puntuamos cada medida"
    )

    dict_scores = return_dict_medidas(dict_medidas)
    path_medidas = os.path.join(path_output, "medidas")
    store_dict_scores(dict_scores, path_output=path_medidas)
    logger.debug(
        "La puntuación de cada medida por provincia ha sido guardada en "
        f"{path_medidas}\n\n...\n\nPasamos a puntuar los items"
    )

    dict_items = return_dict_items(dict_scores)
    path_items = os.path.join(path_output, "items")
    store_dict_scores(dict_items, path_output=path_items)
    logger.debug(
        "La puntuación de cada item por provincia ha sido guardada en "
        f"{path_items}\n\n...\n\nPasamos a puntuar los ambitos"
    )

    dict_ambito = return_dict_ambitos(dict_items, path_taxonomia=path_taxonomia)
    dict_islas = return_dict_islas(dict_ambito)
    dict_ambito = update_keep_old_keys(dict_ambito, dict_islas)
    path_score_ambito = os.path.join(path_output, "score_ambito")
    store_dict_scores(dict_ambito, path_output=path_score_ambito)

    logger.debug(
        "La puntuación de cada ambito ha sido guardada en "
        f"{path_score_ambito}\n\n...\n\nPasamos a guardar la informacion de movilidad"
    )

    path_mobility = os.path.join(path_output, "mobility")
    mobility_report_to_csv(path_output=path_mobility)
    logger.debug(f"La informacion de movilidad ha sido guardada en {path_mobility}\n")


if __name__ == "__main__":
    typer.run(main)
