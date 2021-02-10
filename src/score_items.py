import pandas as pd
import numpy as np
import typer

from src.dictionaries import store_dict_scores, load_dict_scores


def compute_proportion(df: pd.DataFrame, item: str):

    df_sub = df[["fecha", "porcentaje_afectado", item]].copy()

    # Convertimos los NaNs autonomicos/provinciales a 0
    mask_autonomico = df_sub["porcentaje_afectado"] == 100
    df_sub.loc[mask_autonomico, item] = df_sub.loc[mask_autonomico, item].fillna(0)

    # Los otros NaNs, que pertenecen a medidas subprovinciales
    # no aplicadas, se eliminan
    df_sub.dropna(inplace=True)

    porcentaje_general = (
        100
        - df_sub.query("porcentaje_afectado < 100")
        .groupby("fecha")["porcentaje_afectado"]
        .sum()
    )

    mask_general = df_sub["porcentaje_afectado"] == 100
    mask_subprov = df_sub["fecha"].isin(porcentaje_general.index)

    try:
        df_sub.loc[
            mask_general & mask_subprov, "porcentaje_afectado"
        ] = porcentaje_general.values
    except ValueError:
        for fecha, porcentaje in porcentaje_general.items():
            mask_fecha = df_sub["fecha"] == fecha
            mask = mask_fecha & mask_general
            if mask.sum() > 0:
                df_sub.loc[mask, "porcentaje_afectado"] = porcentaje
            else:
                df_sub = df_sub.append(
                    {"fecha": fecha, "porcentaje_afectado": porcentaje, item: 0},
                    ignore_index=True,
                )

    df_sub["ponderado"] = df_sub["porcentaje_afectado"] * df_sub[item] / 100

    score = df_sub.groupby("fecha")["ponderado"].sum()

    return score


def score_items(df: pd.DataFrame):
    df_item = df[["fecha", "porcentaje_afectado"]].copy()

    # Deporte exterior
    df_item["DEX_afor"] = df[["AF.1", "AF.6", "AF.7"]].max(axis=1)
    df_item["DP_cont"] = df[["AF.4", "AF.17"]].max(axis=1)
    df_item["DEX_pub"] = df[["AF.3", "AF.13", "AF.15"]].max(axis=1)

    # Deporte interior
    df_item["DIN_afo"] = df[["AF.1", "AF.2", "AF.5", "AF.12"]].max(axis=1)
    df_item["DIN_pub"] = df[["AF.3", "AF.14", "AF.16"]].max(axis=1)
    df_item["DIN_pisc"] = df[["AF.8", "AF.9"]].max(axis=1)

    # Ceremonias

    # Comercio

    # Colegios

    # Educacion otra

    # Ocio Nocturno
    df_item["OCN_afo"] = np.max(
        [
            df["ON.1"],
            df["ON.2"],
            df["ON.4"],
            (0.7 * df["ON.5"] + 0.3 * df["ON.6"]) * (df["ON.4"] == 0),
        ]
    )
    df_item["OCN_mes"] = df[["ON.1", "ON.2", "ON.10"]].max(axis=1)
    df_item["OCN_hor"] = df[["ON.1", "ON.2", "ON.8"]].max(axis=1)
    df_item["OCN_bai"] = df[["ON.1", "ON.2", "ON.3"]].max(axis=1)
    df_item["OCN_ver"] = df["ON.7"]

    # Cultura
    df_item["CUL_mus"] = np.max(
        [
            df["CD.1"],
            df["CD.6"],
            (0.7 * np.max([df["CD.2"], df["CD.7"]], axis=0) + 0.3 * df["CD.8"])
            * (df["CD.6"] == 0),
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
    df_item["CUL_tor"] = df[["CD.17", "CD.14"]].max(axis=1)
    df_item["CUL_zoo"] = df[["CD.16", "CD.15"]].max(axis=1)

    # Restauración interior
    df_item["RIN_bing"] = df[["LA.1", "LA.2"]].max(axis=1)
    df_item["RIN_binh"] = df[["LA.1", "LA.3"]].max(axis=1)
    df_item["RIN_afo"] = df[["RH.1", "RH.2", "RH.3", "RH.7"]].max(axis=1)
    df_item["RIN_hor"] = df[["RH.1", "RH.2", "RH.3", "RH.5"]].max(axis=1)
    df_item["RIN_mesa"] = df[["RH.1", "RH.2", "RH.3", "RH.9", "RH.11"]].max(axis=1)

    # Restauración exterior
    df_item["REX_afo"] = df[["RH.1", "RH.2", "RH.6"]].max(axis=1)
    df_item["REX_otr"] = df[["RH.1", "RH.2", "RH.9", "RH.10"]].max(axis=1)

    # Distancia social
    df_item["DS_even"] = df[["MV.1", "CD.12", "CD.13"]].max(axis=1)
    df_item["DS_dom"] = df[["MV.1", "MV.2"]].max(axis=1)
    df_item["DS_reun"] = df[["MV.1", "RS.1", "RS.2", "RS.8"]].max(axis=1)
    df_item["DS_tran"] = df[["MV.1", "TP.1"]].max(axis=1)
    df_item["DS_alc"] = df[["MV.1", "RS.6"]].max(axis=1)

    # Movilidad
    df_item["MOV_qued"] = df[["MV.1", "MV.3"]].max(axis=1)
    df_item["MOV_per"] = df[["MV.1", "MV.4"]].max(axis=1)
    df_item["MOV_int"] = df[["MV.1", "MV.7"]].max(axis=1)

    # Trabajo
    df_item["TRA_1"] = df[["TR.1", "TR.2", "TR.3"]].max(axis=1)
    df_item["TRA_2"] = np.max(
        [
            df["TR.8"],
            df["TR.9"],
            (
                0.3 * np.max([df["TR.4"], df["TR.5"]], axis=0)
                + 0.7 * np.max([df["TR.6"], df["TR.7"]], axis=0)
            )
            * (df["TR.9"] == 0),
        ]
    )

    return df_item


def ponderate_items(df_item: pd.DataFrame):

    list_item = df_item.columns.tolist()
    list_item.remove("fecha")
    list_item.remove("porcentaje_afectado")
    dict_ponderado = {}
    for item in list_item:
        dict_ponderado.update({item: compute_proportion(df_item, item)})
    df_ponderado = pd.DataFrame.from_dict(dict_ponderado)

    df_ponderado = df_ponderado.reset_index().rename(columns={"index": "fecha"})

    return df_ponderado


def return_dict_score_items(dict_scores: dict, verbose: bool = True) -> dict:
    dict_items = {}
    dict_items_ponderados = {}

    for provincia, df_sub in dict_scores.items():
        if verbose:
            print(provincia)
        df_item = score_items(df_sub)
        df_ponderado = ponderate_items(df_item)
        dict_items.update({provincia: df_item.set_index("fecha")})
        dict_items_ponderados.update({provincia: df_ponderado.set_index("fecha")})

    return dict_items, dict_items_ponderados


def main(
    path_score_medidas: str = "output/score_medidas",
    path_output: str = "output/score_items",
    path_output_ponderado: str = "output/score_items_ponderado",
):
    dict_scores = load_dict_scores(path_score_medidas)
    dict_items, dict_items_ponderados = return_dict_score_items(dict_scores)
    store_dict_scores(dict_items, path_output=path_output)
    store_dict_scores(dict_items_ponderados, path_output=path_output_ponderado)


if __name__ == "__main__":
    typer.run(main)