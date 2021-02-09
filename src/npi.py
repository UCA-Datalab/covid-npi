import os
from datetime import date

import numpy as np
import pandas as pd
import typer

from src.medidas import load_dict_medidas
from src.taxonomia import return_taxonomia, return_all_medidas

# Define NaN globally to build conditions with NaN
nan = np.nan


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


def build_condicion_no_especifica(lista_medidas):
    condicion = build_condicion_existe(lista_medidas)
    condicion_compuesta = f"({condicion} & (personas == @nan))"
    return condicion_compuesta


def build_condicion_horario(lista_medidas, hora):
    condicion = build_condicion_existe(lista_medidas)
    condicion_compuesta = f"({condicion} & (hora <= {hora}))"
    return condicion_compuesta


def expand_nivel_educacion(df):
    # Split the dataframe in two:
    # df_ed contains only the measures that apply to different education levels
    # df_no_ed contains the rest of measures
    df_ed = df.query(
        "(codigo == 'ED.1') | (codigo == 'ED.2') | (codigo == 'ED.5')"
    ).copy()
    df_no_ed = df.query(
        "(codigo != 'ED.1') & (codigo != 'ED.2') & (codigo != 'ED.5')"
    ).copy()
    try:
        df_ed["niv_edu"] = (
            df_ed["nivel_educacion"]
            .fillna("t")
            .str.replace("\d+", "")
            .str.upper()
            .str[0]
        )
    except AttributeError:
        return df

    df_ed.reset_index(drop=True, inplace=True)
    drop_idx = []

    mask_edu = df_ed["niv_edu"] == "t"

    for i, row in df_ed[mask_edu].iterrows():
        drop_idx += [i]
        for niv_edu in ["B", "U", "I", "P", "S"]:
            new_row = row.copy()
            new_row["niv_edu"] = niv_edu
            df_ed = df_ed.append(new_row)

    df_ed = df_ed.reset_index(drop=True).drop(drop_idx)
    df_ed["codigo"] = df_ed["codigo"] + df_ed["niv_edu"]
    df_ed = df_ed.drop(["niv_edu"], axis=1)

    df_expanded = pd.concat([df_ed, df_no_ed])
    return df_expanded


def score_medidas(df: pd.DataFrame, taxonomia: pd.DataFrame) -> pd.DataFrame:
    df_score = df.copy()
    # Asumimos que por defecto es baja
    df_score["score_medida"] = 0.3

    dict_condicion = {}

    for nivel in ["alto", "medio"]:
        list_condiciones = []
        # Existe
        existe = taxonomia.loc[
            taxonomia[nivel].str.contains("existe"), "codigo"
        ].unique()
        if len(existe) > 0:
            list_condiciones += [build_condicion_existe(existe)]
        # Personas
        for pers in [6, 10, 100]:
            personas_leq = taxonomia.loc[
                taxonomia[nivel].str.contains(f"<={pers}(?!%)", regex=True), "codigo"
            ].unique()
            if len(personas_leq) > 0:
                list_condiciones += [build_condicion_personas(personas_leq, pers)]
        # Personas no especifica
        no_especifica = taxonomia.loc[
            taxonomia[nivel].str.contains("noseespecifica"), "codigo"
        ].unique()
        if len(no_especifica) > 0:
            list_condiciones += [build_condicion_no_especifica(no_especifica)]
        # Porcentaje
        for por in [35]:
            porcentaje_leq = taxonomia.loc[
                taxonomia[nivel].str.contains(f"<={por}%"), "codigo"
            ].unique()
            if len(porcentaje_leq) > 0:
                list_condiciones += [build_condicion_porcentaje(porcentaje_leq, por)]
        # Hora
        for hor in [18]:
            hora_leq = taxonomia.loc[
                (taxonomia[nivel].str.contains(f"antesdelas{hor}:00"))
                | (taxonomia[nivel].str.contains(f"antesoigualquelas{hor}:00")),
                "codigo",
            ].unique()
            if len(hora_leq) > 0:
                list_condiciones += [build_condicion_horario(hora_leq, hor)]
        # All conditions
        condicion = " | ".join(list_condiciones)
        dict_condicion.update({nivel: condicion})

    condicion_alto = dict_condicion["alto"]
    condicion_medio = dict_condicion["medio"]

    mask_alto = df.query(condicion_alto).index
    mask_medio = df.query(condicion_medio).index

    df_score.loc[mask_medio, "score_medida"] = 0.6
    df_score.loc[mask_alto, "score_medida"] = 1

    df_score = expand_nivel_educacion(df_score)

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

    taxonomia = return_taxonomia()
    all_medidas = return_all_medidas()

    for provincia, df_sub in dict_medidas.items():
        df_sub_extended = extend_fecha(df_sub)
        df_score = score_medidas(df_sub_extended, taxonomia)
        assert df_score.max().max() <= 1, "Maximum greater than 1 for {provincia}"
        # Nos aseguramos de que todas las medidas estan en el df
        medidas_missing = list(set(all_medidas) - set(df_score.columns))
        for m in medidas_missing:
            df_score[m] = 0
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
