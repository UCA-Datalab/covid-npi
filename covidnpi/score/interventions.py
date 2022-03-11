import datetime as dt
import warnings

import numpy as np
import pandas as pd
import typer

from covidnpi.utils.dictionaries import (
    store_dict_scores,
    load_dict_interventions,
    store_dict_condicion,
)
from covidnpi.utils.log import logger
from covidnpi.utils.taxonomy import return_taxonomy, return_all_interventions

warnings.simplefilter(action="ignore", category=FutureWarning)

# Define NaN globally to build conditions with NaN
nan = np.nan


def process_hora(df: pd.DataFrame) -> pd.DataFrame:
    """Para poder hacer las comparaciones de hora de cierre,
    sumamos 24h a las primeras horas de la mañana"""
    mask_early = df["hora"] <= 8
    df.loc[mask_early, "hora"] += 24
    return df


def extend_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """Get a row for each date and restriction

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame

    """
    # Extendemos las fechas
    df["fecha"] = df.apply(
        lambda x: pd.date_range(x["fecha_inicio"], x["fecha_fin"]), axis=1
    )
    df_extended = (
        df.explode("fecha")
        .sort_values(["fecha", "provincia"], axis=0)
        .reset_index(drop=True)
    )

    # Truncate up to today
    df_extended = df_extended[df_extended["fecha"] <= dt.datetime.today()]
    return df_extended


def build_condicion_existe(lista_interventions):
    condicion = [
        f"(codigo == '{intervention}')" for intervention in lista_interventions
    ]
    condicion = " | ".join(condicion)
    condicion = f"({condicion})"
    return condicion


def build_condicion_porcentaje(lista_interventions, porcentaje):
    condicion = build_condicion_existe(lista_interventions)
    condicion_compuesta = f"({condicion} & (porcentaje <= {porcentaje}))"
    return condicion_compuesta


def build_condicion_personas(lista_interventions, personas, condition: str = "<="):
    condicion = build_condicion_existe(lista_interventions)
    condicion_compuesta = f"({condicion} & (personas {condition} {personas}))"
    return condicion_compuesta


def build_condicion_no_especifica(lista_interventions):
    condicion = build_condicion_existe(lista_interventions)
    condicion_compuesta = f"({condicion} & (personas == @nan))"
    return condicion_compuesta


def build_condicion_horario(lista_interventions, hora):
    condicion = build_condicion_existe(lista_interventions)
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


def list_missing_codigos(taxonomy: pd.DataFrame, dict_condicion: dict):
    """Avisa de que faltan ciertos codigos en la lista de condiciones"""
    codigos = "-".join([s for s in dict_condicion.values()])
    list_missing = []
    # Filtramos aquellas con bajo == "existe" porque no saldran en la lista
    for codigo in taxonomy.query("bajo != 'existe'")["codigo"].unique():
        if codigo not in codigos:
            list_missing.append(codigo)
    if len(list_missing) > 0:
        logger.error(f"Faltan codigos en condicones: {', '.join(list_missing)}")


def add_score_intervention(
    df: pd.DataFrame,
    taxonomy: pd.DataFrame,
    path_out_conditions: str = "output/dict_condicion.json",
) -> pd.DataFrame:
    df_score = df.copy()
    # Asumimos que por defecto es baja
    df_score["score_intervention"] = 0.2

    dict_condicion = {}

    for nivel in ["alto", "medio"]:
        list_condiciones = []
        # Existe
        existe = taxonomy.loc[taxonomy[nivel].str.contains("existe"), "codigo"].unique()
        if len(existe) > 0:
            list_condiciones.append(build_condicion_existe(existe))
        # Personas
        for pers in [6, 10, 100]:
            for condition in ["<=", "<"]:
                personas_cond = taxonomy.loc[
                    taxonomy[nivel].str.contains(f"{condition}{pers}(?!%)", regex=True),
                    "codigo",
                ].unique()
                if len(personas_cond) > 0:
                    list_condiciones.append(
                        build_condicion_personas(
                            personas_cond, pers, condition=condition
                        )
                    )
        # Personas no especifica
        no_especifica = taxonomy.loc[
            taxonomy[nivel].str.contains("noseespecifica"), "codigo"
        ].unique()
        if len(no_especifica) > 0:
            list_condiciones.append(build_condicion_no_especifica(no_especifica))
        # Porcentaje
        for por in [35]:
            porcentaje_leq = taxonomy.loc[
                taxonomy[nivel].str.contains(f"<={por}%"), "codigo"
            ].unique()
            if len(porcentaje_leq) > 0:
                list_condiciones.append(build_condicion_porcentaje(porcentaje_leq, por))
        # Hora
        for hor in [18]:
            hora_leq = taxonomy.loc[
                (taxonomy[nivel].str.contains(f"antesdelas{hor}:00"))
                | (taxonomy[nivel].str.contains(f"antesoigualquelas{hor}:00")),
                "codigo",
            ].unique()
            if len(hora_leq) > 0:
                list_condiciones.append(build_condicion_horario(hora_leq, hor))
        # All conditions
        condicion = " | ".join(set(list_condiciones))
        dict_condicion.update({nivel: condicion})

    # Store dictionary
    store_dict_condicion(dict_condicion, path_output=path_out_conditions)
    # List missing codigos
    list_missing_codigos(taxonomy, dict_condicion)

    condicion_alto = dict_condicion["alto"]
    condicion_medio = dict_condicion["medio"]

    try:
        mask_alto = df.query(condicion_alto).index
        mask_medio = df.query(condicion_medio).index
    except TypeError:
        raise TypeError(f"Column with unproper type:\n{df.dtypes}")

    df_score.loc[mask_medio, "score_intervention"] = 0.5
    df_score.loc[mask_alto, "score_intervention"] = 1

    # df_score = expand_nivel_educacion(df_score)

    return df_score


def pivot_df_score(df_score: pd.DataFrame):
    df_intervention = df_score[["codigo", "score_intervention"]].pivot(
        columns="codigo", values="score_intervention"
    )
    df_intervention["fecha"] = df_score["fecha"].reset_index(drop=True)
    df_intervention["porcentaje_afectado"] = (
        df_score["porcentaje_afectado"].fillna(100).reset_index(drop=True)
    )
    df_intervention = df_intervention.groupby(["fecha", "porcentaje_afectado"]).max()

    return df_intervention


def score_interventions(
    df: pd.DataFrame,
    taxonomy: pd.DataFrame,
    path_out_conditions: str = "output/dict_condicion.json",
) -> pd.DataFrame:
    """Receives the interventions dataframe and outputs a new dataframe of scores

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of interventions
    taxonomy : pd.DataFrame
        Dataframe with taxonomy data
    path_out_conditions: str, optional
        Path where the extracted conditions are stored, by default "output/dict_condicion.json"

    Returns
    -------
    pd.DataFrame
        Dataframe of scores, each row being a date and each column a intervention
    """
    df_sub = df.copy()
    df_sub = process_hora(df_sub)
    df_sub_extended = extend_fecha(df_sub)
    df_score = add_score_intervention(
        df_sub_extended, taxonomy, path_out_conditions=path_out_conditions
    )
    df_score = pivot_df_score(df_score)
    return df_score


def return_dict_interventions(dict_interventions: dict) -> dict:
    """

    Parameters
    ----------
    dict_interventions : dict

    Returns
    -------
    dict
        Dictionary of scores

    """
    dict_scores = {}

    taxonomy = return_taxonomy()
    all_interventions = return_all_interventions()

    for provincia, df_sub in dict_interventions.items():
        logger.debug(provincia)
        df_score = score_interventions(df_sub, taxonomy)
        # Nos aseguramos de que todas las interventions estan en el df
        interventions_missing = list(set(all_interventions) - set(df_score.columns))
        for m in interventions_missing:
            df_score[m] = np.nan
        dict_scores.update({provincia: df_score})

    return dict_scores


def main(
    path_interventions: str = "output/interventions",
    path_output: str = "output/interventions",
):
    dict_interventions = load_dict_interventions(path_interventions=path_interventions)
    dict_scores = return_dict_interventions(dict_interventions)
    store_dict_scores(dict_scores, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
