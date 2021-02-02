import os

import date
import pandas as pd
import typer

from src.medidas import load_dict_medidas
from src.taxonomia import return_all_medidas


def extend_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """Get a row for each date and restriction"""
    df = df.copy()
    # Reemplazamos ESTADO DE ALARMA por su fecha
    df.loc[df["fecha_fin"] == "ESTADO DE ALARMA", "fecha_fin"] = "2021-05-09"
    # Si no hay fecha de inicio se coge la fecha de publicacion
    df["fecha_inicio"] = df["fecha_inicio"].fillna(df["fecha_publicacion_oficial"])
    # Llenamos los NaN de fecha_fin con el día de hoy
    df["fecha_fin"] = df["fecha_fin"].fillna(pd.Timestamp(date.today()))
    # Correccion
    df.loc[df["fecha_fin"] == "06/112020", "fecha_fin"] = "2020-11-06"
    # Extendemos las fechas
    df["fecha"] = df.apply(
        lambda x: pd.date_range(x["fecha_inicio"], x["fecha_fin"]), axis=1
    )
    df_extended = (
        df.explode("fecha")
        .sort_values(["fecha", "provincia"], axis=0)
        .reset_index(drop=True)
    )
    return df_extended


def build_condicion_existe(lista_medidas):
    condicion = [f"(codigo == '{medida}')" for medida in lista_medidas]
    condicion = " | ".join(condicion)
    condicion = f"({condicion})"
    return condicion


def build_condicion_porcentaje(lista_medidas, porcentaje):
    condicion = build_condicion_existe(lista_medidas)
    condicion_compuesta = f"({condicion} & (porcentaje <= {porcentaje}))"
    return condicion_compuesta


def build_condicion_personas(lista_medidas, personas):
    condicion = build_condicion_existe(lista_medidas)
    condicion_compuesta = f"({condicion} & (personas <= {personas}))"
    return condicion_compuesta


def build_condicion_horario(lista_medidas, hora):
    condicion = build_condicion_existe(lista_medidas)
    condicion_compuesta = f"({condicion} & (hora <= {hora}))"
    return condicion_compuesta


def score_medidas(df: pd.DataFrame) -> pd.DataFrame:
    df_score = df.copy()
    # Asumimos que por defecto es baja
    df_score["score_medida"] = 0.3

    condicion_alto = " | ".join(
        [
            build_condicion_existe(
                [
                    "AF.1",
                    "AF.2",
                    "AF.4",
                    "AF.3",
                    "AF.13",
                    "AF.8",
                    "AF.14",
                    "CD.1",
                    "CD.2",
                    "CD.3",
                    "CD.4",
                    "CD.5",
                    "CD.16",
                    "CD.17",
                    "CE.1",
                    "CE.7",
                    "CO.1",
                    "CO.2",
                    "CO.3",
                    "CO.4",
                    "CO.5",
                    "CO.6",
                    "ON.1",
                    "ON.2",
                    "ON.7",
                    "LA.1",
                    "RH.1",
                    "RH.2",
                    "RH.3",
                    "MV.1",
                    "RS.8",
                    "MV.3",
                    "MV.4",
                    "TR.1",
                    "TR.4",
                    "TR.6",
                    "TR.8",
                ]
            ),
            build_condicion_personas(["RS.1", "RS.2"], 6),
        ]
    )

    condicion_medio = " | ".join(
        [
            build_condicion_porcentaje(
                [
                    "AF.6",
                    "AF.15",
                    "AF.5",
                    "AF.9",
                    "AF.16",
                    "CD.6",
                    "CD.7",
                    "CD.8",
                    "CD.9",
                    "CD.10",
                    "CD.11",
                    "CD.14",
                    "CD.15",
                    "CE.2",
                    "CE.3",
                    "CE.4",
                    "CE.5",
                    "CE.6",
                    "CO.8",
                    "CO.9",
                    "CO.10",
                    "ON.4",
                    "ON.5",
                    "ON.6" "LA.3",
                    "RH.7",
                    "RH.6",
                    "TR.5",
                    "TR.7",
                    "TR.9",
                ],
                35,
            ),
            build_condicion_personas(
                [
                    "AF.6",
                    "AF.7",
                    "AF.5",
                    "AF.17",
                    "AF.12",
                    "ON.10",
                    "RH.9",
                    "RH.10",
                    "RH.11",
                ],
                6,
            ),
            build_condicion_personas(
                ["CE.3", "CE.4", "CE.5", "CE.6", "RS.1", "RS.2"], 10
            ),
            build_condicion_personas(["CD.12", "CD.13"], 100),
            build_condicion_existe(["ED.2", "ED.5", "TR.2"]),
            build_condicion_horario(["RH.5"], 18),
        ]
    )

    mask_alto = df.query(condicion_alto).index
    mask_medio = df.query(condicion_medio).index

    df_score.loc[mask_medio, "score_medida"] = 0.6
    df_score.loc[mask_alto, "score_medida"] = 1

    df_score = (
        df_score[["codigo", "score_medida"]]
        .pivot(columns="codigo", values="score_medida")
        .fillna(0)
    )
    df_score["fecha"] = df["fecha"]
    df_score = df_score.groupby("fecha").max()

    return df_score


def return_dict_scores(dict_medidas: dict) -> dict:
    dict_scores = {}

    all_medidas = return_all_medidas()

    for provincia, df_sub in dict_medidas.items():
        df_sub_extended = extend_fecha(df_sub)
        df_score = score_medidas(df_sub_extended)
        assert df_score.max().max() <= 1, "Maximum greater than 1 for {provincia}"
        # Nos aseguramos de que todas las medidas estan en el df
        missing = list(set(all_medidas) - set(df_score.columns))
        df_score[missing] = 0
        df_score = df_score[all_medidas]
        dict_scores.update({provincia: df_score})

    return dict_scores


def store_dict_scores(dict_scores, path_output: str = "output_scores"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_score in dict_scores.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        df_score.to_csv(path_file)


def main(path_medidas: str = "output_medidas", path_output: str = "output_scores"):
    dict_medidas = load_dict_medidas(path_medidas=path_medidas)
    dict_scores = return_dict_scores(dict_medidas)
    store_dict_scores(dict_scores, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
