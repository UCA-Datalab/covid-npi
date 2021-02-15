import os
import typer

from covidnpi.utils.dictionaries import store_dict_scores, store_dict_medidas
from covidnpi.utils.preprocess import read_npi_and_build_dict
from covidnpi.score.score_medidas import return_dict_score_medidas
from covidnpi.score.score_items import return_dict_score_items


def main(
    path_raw: str = "datos_NPI_2",
    path_taxonomia: str = "datos_NPI/Taxonomía_07022021.xlsx",
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
        Path to taxonomia xlsx file, by default "datos_NPI/Taxonomía_07022021.xlsx"
    path_output : str, optional
        Output folder, by default "output"

    """
    print(f"Leyendo datos crudos de {path_raw}\nAgrupamos por provincia")
    dict_medidas = read_npi_and_build_dict(
        path_data=path_raw, path_taxonomia=path_taxonomia
    )

    # Build output path
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    path_medidas = os.path.join(path_output, "medidas")
    store_dict_medidas(dict_medidas, path_output=path_medidas)
    print(
        f"Las medidas preprocesadas han sido guardadas en {path_medidas}\n...\n"
        f"Ahora puntuamos cada medida"
    )

    dict_scores = return_dict_score_medidas(dict_medidas)
    path_score_medidas = os.path.join(path_output, "score_medidas")
    store_dict_scores(dict_scores, path_output=path_score_medidas)
    print(
        f"La puntuación de cada medida por provincia ha sido guardada en "
        f"{path_score_medidas}\n...\nPasamos a puntuar los items"
    )

    dict_items, dict_items_afectado = return_dict_score_items(
        dict_scores, path_taxonomia=path_taxonomia
    )
    path_score_items = os.path.join(path_output, "score_items")
    path_score_items_afectado = os.path.join(path_output, "score_items_afectado")
    store_dict_scores(dict_items, path_output=path_score_items)
    store_dict_scores(dict_items_afectado, path_output=path_score_items_afectado)
    print(
        f"La puntuación de cada item por provincia ha sido guardada en "
        f"{path_score_items}\nY también calculada por porcentaje afectado, en "
        f"{path_score_items_afectado}"
    )


if __name__ == "__main__":
    typer.run(main)
