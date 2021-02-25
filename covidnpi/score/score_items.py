import numpy as np
import pandas as pd
import typer

from covidnpi.utils.dictionaries import store_dict_scores, load_dict_scores
from covidnpi.utils.taxonomia import return_item_ponderacion, PATH_TAXONOMIA


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
    df_item["DIN_pub"] = df[["AF.3", "AF.14", "AF.16"]].max(axis=1)
    df_item["DIN_pisc"] = df[["AF.8", "AF.9"]].max(axis=1)

    # Ceremonias
    df_item["CER_cult"] = df[["CE.1", "CE.2"]].max(axis=1)
    df_item["CER_cor"] = df[["CE.1", "CE.7"]].max(axis=1)
    df_item["CER_ent"] = np.max(
        [df["CE.9"], (0.7 * df["CE.3"] + 0.3 * df["CE.4"]) * (df["CE.9"] == 0)]
    )
    df_item["CER_otr"] = np.max(
        [df["CE.10"], (0.7 * df["CE.5"] + 0.3 * df["CE.6"]) * (df["CE.10"] == 0)]
    )

    # Comercio
    df_item["COM_afo"] = df[["CO.1", "CO.8"]].max(axis=1)
    df_item["COM_hor"] = df[["CO.1", "CO.7"]].max(axis=1)
    df_item["COM_esp"] = df[["CO.1", "CO.2"]].max(axis=1)
    df_item["COM_fis"] = df[["CO.1", "CO.3"]].max(axis=1)
    df_item["COM_cent"] = df[["CO.4", "CO.9"]].max(axis=1)
    df_item["COM_cczon"] = df[["CO.4", "CO.5"]].max(axis=1)
    df_item["COM_libre"] = df[["CO.1", "CO.6", "CO.10"]].max(axis=1)

    # Colegios
    for n in ["I", "P", "S", "B"]:
        df_item[f"COL_{n}"] = df[[f"ED.1{n}", f"ED.5{n}", f"ED.2{n}"]].max(axis=1)
    df_item["COL"] = (
        df_item[["COL_I", "COL_P", "COL_S", "COL_B"]].fillna(0).mean(axis=1)
    )

    # Educacion otra
    df_item["EDU_uni"] = df[["ED.1U", "ED.5U", "ED.2U"]].max(axis=1)
    df_item["EDU_acad"] = df[["ED.3", "ED.4"]].max(axis=1)

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


def apply_porcentaje_afectado_to_items(df_item: pd.DataFrame):

    list_item = df_item.columns.tolist()
    list_item.remove("fecha")
    list_item.remove("porcentaje_afectado")
    dict_ponderado = {}
    for item in list_item:
        dict_ponderado.update({item: compute_proportion(df_item, item)})
    df_afectado = pd.DataFrame.from_dict(dict_ponderado)

    # Fill missing dates with 0's
    idx = pd.date_range(df_afectado.index.min(), df_afectado.index.max())
    df_afectado = df_afectado.reindex(idx, fill_value=0)

    # "fecha" to column
    df_afectado = df_afectado.reset_index().rename(columns={"index": "fecha"})

    return df_afectado


def score_ponderada(df_afectado: pd.DataFrame, path_taxonomia=PATH_TAXONOMIA):
    ponderacion = return_item_ponderacion(path_taxonomia=path_taxonomia)
    list_ambito = ponderacion["ambito"].unique()
    for ambito in list_ambito:
        pon_sub = ponderacion.query(f"ambito == '{ambito}'")
        pesos = pon_sub["ponderacion"].values
        items = pon_sub["nombre"]
        df_afectado[ambito] = (df_afectado[items] * pesos).sum(axis=1).div(pesos.sum())
    return df_afectado


def return_dict_score_items(
    dict_scores: dict,
    path_taxonomia: str = PATH_TAXONOMIA,
    verbose: bool = True,
) -> tuple:
    dict_items = {}
    dict_ambito = {}

    for provincia, df_sub in dict_scores.items():
        if verbose:
            print(provincia)
        df_item = score_items(df_sub)
        df_afectado = apply_porcentaje_afectado_to_items(df_item)
        df_afectado = score_ponderada(df_afectado, path_taxonomia=path_taxonomia)
        dict_items.update({provincia: df_item.set_index("fecha")})
        dict_ambito.update({provincia: df_afectado.set_index("fecha")})

    return dict_items, dict_ambito


def main(
    path_score_medidas: str = "output/score_medidas",
    path_output: str = "output/score_items",
    path_output_ponderado: str = "output/score_ambito",
    path_taxonomia: str = PATH_TAXONOMIA,
):
    dict_scores = load_dict_scores(path_score_medidas)
    dict_items, dict_ambito = return_dict_score_items(
        dict_scores, path_taxonomia=path_taxonomia
    )
    store_dict_scores(dict_items, path_output=path_output)
    store_dict_scores(dict_ambito, path_output=path_output_ponderado)


if __name__ == "__main__":
    typer.run(main)
