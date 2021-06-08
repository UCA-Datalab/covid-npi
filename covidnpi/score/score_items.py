import datetime as dt

import numpy as np
import pandas as pd
import typer

from covidnpi.utils.dictionaries import store_dict_scores, load_dict_scores
from covidnpi.utils.log import logger


def score_items(df: pd.DataFrame):
    # "fecha" and "porcentaje_afectado" must be columns
    # If they are index, convert to columns
    try:
        df_item = df[["fecha", "porcentaje_afectado"]].copy()
    except KeyError:
        df = df.reset_index().copy()
        df_item = df[["fecha", "porcentaje_afectado"]].copy()

    # Deporte exterior
    df_item["DEX_afor"] = df[["AF.1", "AF.6", "AF.7"]].max(axis=1)
    df_item["DP_cont"] = df[["AF.4", "AF.17"]].max(axis=1)
    df_item["DEX_pub"] = df[["AF.3", "AF.13", "AF.15"]].max(axis=1)

    # Deporte interior
    df_item["DIN_afo"] = df[["AF.1", "AF.2", "AF.5", "AF.12"]].max(axis=1)
    df_item["DIN_grupo"] = df[["AF.4", "AF.17"]].max(axis=1)
    df_item["DIN_pub"] = df[["AF.3", "AF.14", "AF.16"]].max(axis=1)

    # Ceremonias
    df_item["CER_cult"] = df[["CE.1", "CE.2"]].max(axis=1)
    df_item["CER_cor"] = df[["CE.1", "CE.7"]].max(axis=1)
    df_item["CER_ent_int"] = df[["CE.3", "CE.9"]].max(axis=1)
    df_item["CER_ent_ext"] = df[["CE.4", "CE.9"]].max(axis=1)
    df_item["CER_otro_int"] = df[["CE.5", "CE.10"]].max(axis=1)
    df_item["CER_otro_ext"] = df[["CE.6", "CE.10"]].max(axis=1)

    # Comercio
    df_item["COM_afo"] = df[["CO.1", "CO.8"]].max(axis=1)
    df_item["COM_hor"] = df[["CO.1", "CO.7"]].max(axis=1)
    df_item["COM_esp"] = df[["CO.1", "CO.2"]].max(axis=1)
    df_item["COM_fis"] = df[["CO.1", "CO.3"]].max(axis=1)
    df_item["COM_cent"] = df[["CO.1", "CO.4", "CO.9", "CO.8"]].max(axis=1)
    df_item["COM_cczon"] = df[["CO.1", "CO.4", "CO.5"]].max(axis=1)
    df_item["COM_libre"] = df[["CO.1", "CO.6", "CO.10"]].max(axis=1)

    # Cultura
    df_item["CUL_mus"] = np.max(
        [
            df["CD.1"],
            (
                0.5 * np.max([df["CD.2"], df["CD.7"], df["CD.6"]], axis=0)
                + 0.5 * np.max([df["CD.8"], df["CD.6"]], axis=0)
            ),
        ]
    )
    df_item["CUL_cin"] = np.max(
        [
            df["CD.3"],
            (0.7 * np.max([df["CD.4"], df["CD.9"]], axis=0) + 0.3 * df["CD.10"])
            * (df["CD.3"] == 0),
        ]
    )
    df_item["CUL_sal"] = df[["CD.5", "CD.11"]].max(axis=1)
    df_item["CUL_tor"] = df[["CD.3", "CD.17", "CD.14"]].max(axis=1)
    df_item["CUL_zoo"] = df[["CD.3", "CD.16", "CD.15"]].max(axis=1)

    # Restauración interior
    df_item["RIN_afo"] = np.max(
        [
            df[["RH.1", "RH.2", "RH.3"]].max(axis=1),
            df[["RH.4", "RH.7"]].sum(axis=1)
            * df[["RH.1", "RH.2", "RH.3"]].isna().all(axis=1),
        ]
    )
    df_item["RIN_hor"] = df[["RH.1", "RH.2", "RH.3", "RH.5"]].max(axis=1)
    df_item["RIN_mesa"] = df[["RH.1", "RH.2", "RH.3", "RH.9", "RH.11"]].max(axis=1)

    # Restauración exterior
    df_item["REX_afo"] = df[["RH.1", "RH.2", "RH.6"]].max(axis=1)
    df_item["REX_hor"] = df[["RH.1", "RH.2", "RH.5"]].max(axis=1)
    df_item["REX_otr"] = df[["RH.1", "RH.2", "RH.9", "RH.10"]].max(axis=1)

    # Distancia social
    df_item["DS_even"] = df[["MV.1", "CD.12", "CD.13"]].max(axis=1)
    df_item["DS_dom"] = df[["MV.1", "MV.2"]].max(axis=1)
    df_item["DS_reun"] = np.max(
        [
            df[["MV.1", "RS.1"]].max(axis=1),
            df[["RS.2", "RS.3", "RS.8"]].mean(axis=1) * df["RS.1"].isna(),
        ]
    )
    df_item["DS_tran"] = df[["MV.1", "TP.1"]].max(axis=1)

    # Movilidad
    df_item["MOV_qued"] = df[["MV.1", "MV.3"]].max(axis=1)
    df_item["MOV_per"] = df[["MV.1", "MV.4"]].max(axis=1)
    df_item["MOV_int"] = df[["MV.1", "MV.7"]].max(axis=1)

    # Truncate up to today
    df_item = df_item[df_item["fecha"] <= dt.datetime.today()]

    return df_item


def return_dict_score_items(
    dict_scores: dict,
    verbose: bool = True,
) -> dict:
    dict_items = {}

    for provincia, df_sub in dict_scores.items():
        if verbose:
            logger.debug(provincia)
        df_item = score_items(df_sub)
        dict_items.update({provincia: df_item.set_index("fecha")})

    return dict_items


def main(
    path_score_medidas: str = "output/score_medidas",
    path_output: str = "output/score_items",
):
    dict_scores = load_dict_scores(path_score_medidas)
    dict_items = return_dict_score_items(dict_scores)
    store_dict_scores(dict_items, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
