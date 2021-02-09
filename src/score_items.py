import pandas as pd
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

    return df_item


def ponderate_items(df_item: pd.DataFrame):

    list_item = df_item.columns.tolist()
    list_item.remove("fecha")
    list_item.remove("porcentaje_afectado")
    dict_ponderado = {}
    for item in list_item:
        dict_ponderado.update(
            {item: compute_proportion(df_item, item)}
        )
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
