import pandas as pd
import typer
from covidnpi.utils.dictionaries import load_dict_scores, store_dict_scores
from covidnpi.utils.log import logger
from covidnpi.utils.taxonomia import PATH_TAXONOMY, return_item_ponderacion


def compute_proportion(df: pd.DataFrame, item: str):
    """Calcula la score ponderada de un item concreto, teniendo en cuenta las medidas
    subprovinciales. Devuelve un dataframe con una sola fila por fecha"""

    df_sub = df[["fecha", "porcentaje_afectado", item]].copy()

    # Convertimos los NaNs en score a nivel autonomicos/provinciales a 0
    mask_autonomico = df_sub["porcentaje_afectado"] == 100
    df_sub.loc[mask_autonomico, item] = df_sub.loc[mask_autonomico, item].fillna(0)

    # Los otros NaNs, que pertenecen a medidas subprovinciales no aplicadas, se eliminan
    df_sub.dropna(inplace=True)

    # Calculamos el porcentaje de la provincia que es afectado de manera general
    # (cuando se dan medidas subprovinciales)
    porcentaje_general = (
        100
        - df_sub.query("porcentaje_afectado < 100")
        .groupby("fecha")["porcentaje_afectado"]
        .sum()
    )
    # Avisamos si hay sumas de porcentajes que superan el 100
    list_dates = [
        d.strftime("%d-%m-%Y") for d in porcentaje_general[porcentaje_general < 0].index
    ]
    if len(list_dates) > 0:
        logger.warning(
            f"La suma de porcentajes para {item} supera 100 en: {', '.join(list_dates)}"
        )
        porcentaje_general[porcentaje_general < 0] = 0

    # Identificamos las medidas que se han aplicado exclusivamente con caracter general
    mask_general = df_sub["porcentaje_afectado"] == 100
    # Identificamos las medidas que han tenido caracter subprovincial
    mask_subprov = df_sub["fecha"].isin(porcentaje_general.index)

    try:
        # Para las medidas que han tenido caracter subprovincial, cambiamos el porcentaje
        # general de 100 a (100 - subprovincial)
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

    # Se pondera la score de cada item = score * porcentaje que afecta
    df_sub["ponderado"] = df_sub["porcentaje_afectado"] * df_sub[item]

    # Agrupamos por dia, sumando las score ponderadas
    score = (
        df_sub.groupby("fecha")["ponderado"].sum()
        / df_sub.groupby("fecha")["porcentaje_afectado"].sum()
    )

    return score


def apply_porcentaje_afectado_to_items(df_item: pd.DataFrame):
    """Calcula la score ponderada de todos los item, teniendo el cuenta medidas
    subprovinciales. Devuelve un dataframe con una sola fila por fecha"""

    list_item = df_item.columns.tolist()
    try:
        list_item.remove("fecha")
    except ValueError:
        df_item = df_item.reset_index()
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


def score_ponderada(df_afectado: pd.DataFrame, path_taxonomia=PATH_TAXONOMY):
    """Calcula la score de cada ambito a partir de sus item"""
    ponderacion = return_item_ponderacion(path_taxonomia=path_taxonomia)
    list_ambito = ponderacion["ambito"].unique()
    for ambito in list_ambito:
        pon_sub = ponderacion.query(f"ambito == '{ambito}'")
        pesos = pon_sub["ponderacion"].values
        items = pon_sub["nombre"]
        df_afectado[ambito] = (df_afectado[items] * pesos).sum(axis=1).div(pesos.sum())
        # Max value is 1
        # assert df_afectado[ambito].max() <= 1, f"La puntuacion de {ambito} supera 1"
    return df_afectado


def return_dict_ambitos(
    dict_items: dict,
    path_taxonomia: str = PATH_TAXONOMY,
    verbose: bool = True,
) -> dict:
    dict_ambito = {}

    for provincia, df_item in dict_items.items():
        if verbose:
            logger.debug(provincia)
        df_afectado = apply_porcentaje_afectado_to_items(df_item)
        df_afectado = score_ponderada(df_afectado, path_taxonomia=path_taxonomia)
        dict_ambito.update({provincia: df_afectado.set_index("fecha")})

    return dict_ambito


def main(
    path_items: str = "output/items",
    path_output_ponderado: str = "output/score_ambito",
    path_taxonomia: str = PATH_TAXONOMY,
):
    dict_items = load_dict_scores(path_items)
    dict_ambito = return_dict_ambitos(dict_items, path_taxonomia=path_taxonomia)
    store_dict_scores(dict_ambito, path_output=path_output_ponderado)


if __name__ == "__main__":
    typer.run(main)
