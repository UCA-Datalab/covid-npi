import os

import numpy as np
import pandas as pd
import typer
import xlrd

from covidnpi.utils.dictionaries import store_dict_medidas
from covidnpi.utils.logging import logger, raise_type_warning
from covidnpi.utils.taxonomia import return_all_medidas, PATH_TAXONOMIA

LIST_BASE_SHEET = ["base", "base-regional-provincias", "BASE"]

DICT_PORCENTAJE = {
    "cantalejo": 2,
    "carrascaldelrio": 0.1,
    "arandadeduero": 9.1,
    "sotillodelaribera": 0.1,
    "iscar": 1.2,
    "pedrajassanesteban": 0.6,
    "pesqueradeduero": 0.1,
}

DICT_FILL_PROVINCIA = {
    "CEU": "ceuta",
    "MEL": "melilla",
    "RIO": "rioja_la",
}

DICT_COL_RENAME = {
    "cod_con": "codigo",
    "unidad_de_medida": "unidad",
    "%_afectado_(si_subprovincial;_min_25%)": "porcentaje_afectado",
    "%_afectado_(si_subprovincial;_min_10%)": "porcentaje_afectado",
}

LIST_COL_TEXT = [
    "ambito",
    "comunidad_autonoma",
    "provincia",
    "unidad",
    "nivel_educacion",
]

DICT_UNIDAD_RENAME = {
    "hora (en formato 24h)": "hora",
    "hora (formato 24h)": "hora",
    "hora_(en_formato_24h)": "hora",
    "hora_(formato_24h)": "hora",
    "horario": "hora",
    "horas": "hora",
    "pesonas": "personas",
    "personas ": "personas",
    "personas exterior": "personas",
    "a partir de personas": "personas",
    "personas por grupo": "personas",
    "mesas": "personas",
    "porcentaje de puestos": "porcentaje",
    "porcentaje plazas en pie": "porcentaje",
    "aforo": "porcentaje",
    "p": "porcentaje",
    "grupos convivencia": np.nan,
    "m2": np.nan,
    "metros": np.nan,
    "NA": np.nan,
}

LIST_UNIDAD_FLOAT = ["personas", "porcentaje"]

DICT_ADD_PROVINCE = {
    "palencia": "cyl",
    "soria": "cyl",
    "valencia": "comunidad_valenciana",
    "castellon": "comunidad_valenciana",
    "gran_canaria": "canarias",
    "alava": "pais_vasco",
    "guipuzcoa": "pais_vasco",
    "vizcaya": "pais_vasco",
}

DICT_PROVINCE_RENAME = {"a_coruna": "coruna_la", "cyl": ""}
DICT_CCAA_RENAME = {"autonomico": np.nan}


def _raise_missing_column(df: pd.DataFrame, col: str):
    "Raises KeyError related to missing column"
    raise KeyError(f"Falta columna '{col}' en columnas: " f"{', '.join(df.columns)}")


def clean_pandas_str(series: pd.Series):
    series_cleaned = (
        series.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("_$", "")
        # .str.replace("%_afectado*$", "porcentaje_afectado")
    )
    return series_cleaned


def read_npi_data(
    path_com: str,
    col_rename: dict = None,
    province_rename: dict = None,
    ccaa_rename: dict = None,
    list_col_text: list = None,
) -> pd.DataFrame:
    """Read the data contained in a xlsm file"""

    if col_rename is None:
        col_rename = DICT_COL_RENAME
    if province_rename is None:
        province_rename = DICT_PROVINCE_RENAME
    if ccaa_rename is None:
        ccaa_rename = DICT_CCAA_RENAME
    if list_col_text is None:
        list_col_text = LIST_COL_TEXT

    for sheet in LIST_BASE_SHEET:
        try:
            df = pd.read_excel(path_com, sheet_name=sheet)
            break
        except xlrd.biffh.XLRDError:
            pass
    else:
        xl = pd.ExcelFile(path_com)
        raise KeyError(f"File {path_com} does not have base sheet: {xl.sheet_names}")

    # Homogenize column names
    df.columns = clean_pandas_str(df.columns)
    df = df.rename(col_rename, axis=1)
    # Drop columns named "unnamed"
    drop_cols = [col for col in df.columns if col.startswith("unnamed")]
    df = df.drop(drop_cols, axis=1)

    # Preprocesar texto
    for col in list_col_text:
        try:
            df[col] = clean_pandas_str(df[col])
        except AttributeError:
            logger.warning(f"Columna vacia: '{col}'")
        except KeyError:
            logger.error(f"Falta columna: '{col }'")
    # Para el codigo hacemos mas
    df["codigo"] = df["codigo"].fillna(df["cod_gen"]).replace({" ": ""})
    # Rellenamos NaNs en comunidad autonoma
    try:
        df["comunidad_autonoma"] = df["comunidad_autonoma"].replace(ccaa_rename)
        df["comunidad_autonoma"] = df["comunidad_autonoma"].fillna(
            df["comunidad_autonoma"].value_counts().index[0]
        )
    except KeyError:
        _raise_missing_column(df, "comunidad_autonoma")
    # Remplazamos nombres de provincia
    df["provincia"] = (
        df["provincia"].fillna("").replace(province_rename).replace({"": np.nan})
    )

    # Algunas provincias no rellenan la columna "provincia", la rellenamos nosotros
    for key, value in DICT_FILL_PROVINCIA.items():
        if f"Medidas_{key}" in path_com:
            df["provincia"] = df["provincia"].fillna(value)
    return df


def read_npi_folder(path_data: str) -> pd.DataFrame:
    list_df = []

    for file in os.listdir(path_data):
        path_file = os.path.join(path_data, file)
        try:
            df = read_npi_data(path_file)
        except IsADirectoryError:
            continue
        except KeyError:
            logger.warning(f"File {file} could not be opened as province")
            continue
        list_df += [df]

    df = pd.concat(list_df).reset_index(drop=True)
    return df


def gen_cod(prefix, maximo, missing=()):
    """Returns a list of the codes for a given range"""
    lista = set(range(1, maximo + 1)) - set(missing)
    return [prefix + "." + str(n) for n in lista]


def filter_relevant_medidas(df: pd.DataFrame, path_taxonomia: str = PATH_TAXONOMIA):
    all_medidas = return_all_medidas(path_taxonomia=path_taxonomia)
    mask_medidas = df["codigo"].isin(all_medidas)
    df_new = df[mask_medidas]
    dropped = sorted(df.loc[~mask_medidas, "codigo"].astype(str).unique())
    logger.debug(f"Las medidas ignoradas son: {', '.join(dropped)}")
    return df_new


def rename_unidad(df, rename: dict = None):
    if rename is None:
        rename = DICT_UNIDAD_RENAME

    df = df.copy()

    # If any value contains the exact word, change value to word
    list_rename = set(rename.values())
    for word in list_rename:
        if type(word) is float:
            continue
        mask_word = df["unidad"].fillna("NA").str.contains(word, case=False)
        df.loc[mask_word, "unidad"] = word

    # Rename the rest
    df["unidad"] = df["unidad"].replace(rename)
    return df


def format_hora(df):
    df = df.copy()
    # Join all the columns named "hora"
    df_sub = df.query("codigo == 'RH.5'")["hora"].fillna(0).astype(str).str[:2]
    try:
        hora = df_sub.astype(int)
    except ValueError:
        hora = pd.to_numeric(df_sub, errors="coerce")
        list_idx = df_sub[hora.isna()].dropna().index.tolist()
        raise_type_warning(df, list_idx, "hora")

        hora = hora.fillna(0).astype(int)

    hora[hora <= 6] = hora[hora <= 6] + 24
    df["hora"] = hora.astype(int)
    return df


def format_porcentaje_afectado(df: pd.DataFrame):
    df = df.copy()
    # If the column is a string, convert city names to values
    try:
        df["porcentaje_afectado"] = (
            df["porcentaje_afectado"]
            .str.lower()
            .str.replace(" ", "")
            .str.replace(",", ".")
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .replace(DICT_PORCENTAJE)
        )
    except KeyError:
        _raise_missing_column(df, "porcentaje_afectado")
    except AttributeError:
        pass
    try:
        df["porcentaje_afectado"] = df["porcentaje_afectado"].astype(float)
    except TypeError:
        logger.warning(f"porcentaje_afectado is not a float!")
    except ValueError:
        porc_old = df["porcentaje_afectado"].copy()
        porc = pd.to_numeric(df["porcentaje_afectado"], errors="coerce")
        list_idx = porc_old[porc.isna()].dropna().index.tolist()
        raise_type_warning(df, list_idx, "porcentaje_afectado")
        df["porcentaje_afectado"] = porc
    # Avisar si los valores de porcentaje nunca superan 1
    if df["porcentaje_afectado"].dropna().max() <= 1:
        # porc = (porc * 100).astype(float)
        logger.warning("Los valores de 'porcentaje_afectado' nunca superan 1")
    # Round to one decimal
    new_col = df["porcentaje_afectado"].astype(float).round(1)

    df["porcentaje_afectado"] = new_col.round(1)
    return df


def pivot_unidad_valor(df: pd.DataFrame, list_float: tuple = None) -> pd.DataFrame:
    """Pivot the column unidad so that we get one column per category"""
    if list_float is None:
        list_float = LIST_UNIDAD_FLOAT

    # Pasamos las categorias de la columna "unidad" a columnas con valor "valor"
    df_cat = df[["unidad", "valor"]].pivot(columns="unidad", values="valor")
    df_cat = df_cat.loc[:, df_cat.columns.notnull()]
    for col in list_float:
        try:
            df_cat[col] = df_cat[col].astype(float)
        except ValueError:
            df_old = df_cat[col].copy()
            df_cat[col] = pd.to_numeric(df_cat[col], errors="coerce")
            list_idx = df_old[df_cat[col].isna()].dropna().index.tolist()
            raise_type_warning(df, list_idx, "valor")
        except TypeError:
            df_old = df_cat[col].copy()
            df_cat[col] = pd.to_numeric(df_cat[col], errors="coerce")
            list_idx = df_old[df_cat[col].isna()].dropna().index.tolist()
            raise_type_warning(df, list_idx, "valor", typing="fecha")

    df = df.join(df_cat).drop(["unidad", "valor"], axis=1)

    df = format_hora(df)
    return df


def return_dict_provincia(df: pd.DataFrame, dict_add: dict = None) -> dict:
    if dict_add is None:
        dict_add = DICT_ADD_PROVINCE
    df_ccaa = df.groupby(["comunidad_autonoma", "provincia"]).size().reset_index()

    dict_provincia = dict(zip(df_ccaa["provincia"], df_ccaa["comunidad_autonoma"]))

    dict_provincia.update(dict_add)
    return dict_provincia


def return_dict_medidas(df: pd.DataFrame) -> dict:
    dict_provincia = return_dict_provincia(df)

    dict_medidas = {}

    for provincia, ccaa in dict_provincia.items():
        df_sub = (
            df.query(
                f"(provincia == '{provincia}') |"
                f"((comunidad_autonoma == '{ccaa}') "
                f"& (ambito == 'autonomico'))"
            )
            .copy()
            .reset_index(drop=True)
        )
        if not df_sub.empty:
            dict_medidas.update({provincia: df_sub})

    return dict_medidas


def read_npi_and_build_dict(
    path_data: str = "datos_NPI_2",
    path_taxonomia: str = PATH_TAXONOMIA,
):
    dict_medidas = {}
    for file in os.listdir(path_data):
        logger.debug(f"\n................\n{file}")
        path_file = os.path.join(path_data, file)
        try:
            df = read_npi_data(path_file)
        except IsADirectoryError:
            continue
        except KeyError:
            logger.error(f"File {file} could not be opened as province")
            continue
        # Filtramos las medidas relevantes
        df_filtered = filter_relevant_medidas(df, path_taxonomia=path_taxonomia)
        # Renombramos la columna unidad
        df_renamed = rename_unidad(df_filtered)
        # Formateamos "porcentaje afectado"
        df_renamed = format_porcentaje_afectado(df_renamed)
        # Pivotamos la columna "unidad" y le asignamos a cada categoría
        # su correspondiente "valor"
        df_pivot = pivot_unidad_valor(df_renamed)
        # Construimos el diccionario de medidas y lo guardamos
        dict_update = return_dict_medidas(df_pivot)
        dict_medidas.update(dict_update)
        logger.debug(f"................\n")
    return dict_medidas


def main(
    path_data: str = "datos_NPI",
    path_taxonomia: str = PATH_TAXONOMIA,
    path_output: str = "output/medidas",
):
    """Reads the raw data, in path_data, preprocess it and stores the results in
    path_output

    Parameters
    ----------
    path_data : str, optional
    path_taxonomia : str, optional
    path_output : str, optional

    """
    dict_medidas = read_npi_and_build_dict(
        path_data=path_data, path_taxonomia=path_taxonomia
    )
    store_dict_medidas(dict_medidas, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
