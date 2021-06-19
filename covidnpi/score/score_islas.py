from functools import reduce

import pandas as pd
from covidnpi.utils.log import logger
from covidnpi.utils.regions import ISLA_TO_PERCENTAGE


def aggregate_score_isles(dict_islas: dict, dict_ambito: dict) -> pd.DataFrame:
    list_df = []
    for isle, percentage in dict_islas.items():
        try:
            list_df.append(dict_ambito[isle].copy() * percentage)
        except KeyError:
            raise KeyError(f"Falta la isla: {isle}")
    return reduce(lambda x, y: x.add(y, fill_value=0), list_df)


def return_dict_score_islas(dict_ambito: dict) -> dict:
    dict_ccaa = {}
    # Ensure the isles of each group are present
    # If so, perform grouping operation
    for ccaa, dict_islas in ISLA_TO_PERCENTAGE.items():
        logger.debug(ccaa)
        try:
            df = aggregate_score_isles(dict_islas, dict_ambito)
            dict_ccaa.update({ccaa: df})
        except KeyError as er:
            logger.error(f"No se pudo calcular {ccaa}. {er}")
            continue
    return dict_ccaa
