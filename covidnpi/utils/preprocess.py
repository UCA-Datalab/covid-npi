import os
from datetime import date

import numpy as np
import pandas as pd
import typer
import xlrd

from covidnpi.utils.dictionaries import store_dict_provincia_to_interventions
from covidnpi.utils.log import (
    logger,
    raise_type_warning,
    raise_value_warning,
    raise_missing_warning,
)
from covidnpi.utils.taxonomy import return_all_interventions, PATH_TAXONOMY
from covidnpi.utils.regions import (
    DICT_RENAME_PROVINCIA_LOWER,
    DICT_FILL_PROVINCIA_LOWER,
)

LIST_BASE_SHEET = ["base", "base-regional-provincias", "BASE", "Base"]

DICT_PORCENTAJE = {
    "cantalejo": 2,
    "carrascaldelrio": 0.1,
    "arandadeduero": 9.1,
    "sotillodelaribera": 0.1,
    "iscar": 1.2,
    "pedrajassanesteban": 0.6,
    "pesqueradeduero": 0.1,
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
    "horario": "hora",
    "pesonas": "personas",
    "personas ": "personas",
    "mesas": "personas",
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

DICT_CCAA_RENAME = {"autonomico": np.nan}

LIST_INTERVENTIONS_NO_HORA = ["MV.3", "MV.4", "MV.7"]

DICT_FECHA_RENAME = {"06/112020": "2020-11-06", "ESTADO DE ALARMA": "2021-05-09"}

LIST_COLS_OUTPUT = [
    "comunidad_autonoma",
    "provincia",
    "codigo",
    "fecha_inicio",
    "fecha_fin",
    "ambito",
    "porcentaje_afectado",
    "porcentaje",
    "personas",
    "hora",
    "nivel_educacion",
]


def _raise_missing_column(df: pd.DataFrame, col: str):
    """Raises KeyError related to missing column"""
    raise KeyError(f"Missing column '{col}' in columns: " f"{', '.join(df.columns)}")


def clean_pandas_str(series: pd.Series):
    """Homogenizes a pandas series of string type"""
    series_cleaned = (
        series.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("_$", "")
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
        province_rename = DICT_RENAME_PROVINCIA_LOWER
    if ccaa_rename is None:
        ccaa_rename = DICT_CCAA_RENAME
    if list_col_text is None:
        list_col_text = LIST_COL_TEXT

    for sheet in LIST_BASE_SHEET:
        try:
            # Read excel - dates are parsed automatically
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
            logger.warning(f"Empty column: '{col}'")
        except KeyError:
            logger.error(f"Missing column: '{col }'")
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
    if df["provincia"].isnull().all():
        for key, value in DICT_FILL_PROVINCIA_LOWER.items():
            if f"Medidas_{key}" in path_com:
                df["provincia"] = df["provincia"].fillna(value)
                logger.warning(f"Column 'provincia' has been filled with '{value}'.")
                break
        else:
            raise ValueError("Unable to fill column 'provincia'.")
    return df


def filter_relevant_interventions(
    df: pd.DataFrame, path_taxonomy: str = PATH_TAXONOMY
) -> pd.DataFrame:
    """Remove the interventions in `df` not appearing in the taxonomy."""
    all_interventions = return_all_interventions(path_taxonomy=path_taxonomy)
    mask_interventions = df["codigo"].isin(all_interventions)
    df_new = df[mask_interventions]
    dropped = sorted(df.loc[~mask_interventions, "codigo"].astype(str).unique())
    logger.debug(f"The following interventions have been ignored: {', '.join(dropped)}")
    return df_new


def process_fecha(
    df: pd.DataFrame, dict_rename: dict = None, fillna_date_end: str = "today"
) -> pd.DataFrame:
    """Defines a starting and end date for each province

    Parameters
    ----------
    df : pandas.DataFrame
    dict_rename : dict, optional
    fillna_date_end : str, optional
        Defines how we fill the NaNs in fecha_fin column, by default "today":
        - "today": NaNs are changed to today date
        - "start": NaNs are changed to fecha_inicio date

    Returns
    -------
    pandas.DataFrame

    """
    if dict_rename is None:
        dict_rename = DICT_FECHA_RENAME
    # Do not modify the original dataframe
    df = df.copy()
    # Rename strings
    for col in ["fecha_inicio", "fecha_fin"]:
        try:
            df[col] = df[col].replace(dict_rename)
        except TypeError:
            continue
    # Si no hay fecha de inicio se coge la fecha de publicacion, y sino la fecha de
    # inicio de la cuarentena
    list_idx = [str(i + 2) for i in df[df["fecha_inicio"].isna()].index]
    df["fecha_inicio"] = (
        df["fecha_inicio"].fillna(df["fecha_publicacion_oficial"]).fillna("2020-03-15")
    )
    if len(list_idx) > 0:
        logger.warning(
            f"The following rows are missing a start date, "
            f"we take the publication date. If both are missing, "
            f"we take the starting date of the quarantine: {', '.join(list_idx)}"
        )

    # Si no hay fecha final, se pone el dia de hoy o la ultima fecha registrada
    list_idx = [str(i + 2) for i in df[df["fecha_fin"].isna()].index]
    if (len(list_idx) > 0) and ("today" in fillna_date_end.lower()):
        # Llenamos los NaN de fecha_fin con el día de hoy
        df["fecha_fin"] = df["fecha_fin"].fillna(pd.Timestamp(date.today()))
        logger.warning(
            f"The following rows are missing an end date, "
            f"we take today as end date: {', '.join(list_idx)}"
        )
    elif (len(list_idx) > 0) and ("start" in fillna_date_end.lower()):
        # Llenamos los NaN de fecha_fin con fecha_inicio
        df["fecha_fin"] = df["fecha_fin"].fillna(df["fecha_inicio"])
    elif len(list_idx) > 0:
        raise ValueError(f"fillna_date_end not valid: {fillna_date_end}")
    return df


def rename_unidad(df, rename: dict = None) -> pd.DataFrame:
    """Rename the values of column 'unidad'"""
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

    # Listamos los valores de unidad que no se corresponden a los esperados
    list_unidad = df["unidad"].dropna().astype(str).unique()
    list_unidad = sorted(set(list_unidad) - list_rename)
    if len(list_unidad) > 0:
        logger.warning(
            f"Column 'unidad' contains unexpected values: " f"{', '.join(list_unidad)}"
        )
    return df


def format_hora(df: pd.DataFrame) -> pd.DataFrame:
    """Formats the 'hora' column to datetime"""
    # If "hora" is empty, return original
    if df["hora"].isnull().all():
        return df
    # We do not want to modify the original dataframe
    df = df.copy()
    # Take the column "hora" as a string series
    hora = df["hora"].dropna().astype(str).str.replace(" ", "").copy()
    # Change ranges HH:MM-HH:MM to last HH:MM
    mask_range = hora.str.contains(
        "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    ).fillna(False)
    hora[mask_range] = hora[mask_range].str.split("-").str[-1] + ":00"
    # Take hour
    minute = hora.str.split(":").str[1]
    hora = hora.str.split(":").str[0]
    # Force numeric
    hora = pd.to_numeric(hora, errors="coerce")
    minute = pd.to_numeric(minute, errors="coerce")
    # Sum minutes to hora
    hora += minute / 60
    # Check if some original data is missing
    list_idx = df[hora.isna() & ~df["hora"].isna()].index
    raise_missing_warning(df, list_idx, "hora")
    df["hora"] = hora
    return df


def format_porcentaje_afectado(df: pd.DataFrame) -> pd.DataFrame:
    """Formats the column 'porcentaje_afectado'"""
    df = df.copy()
    # En algunos cases aparece el nombre de una zona en lugar del porcentaje
    # Convertimos esos cases a su porcentaje correspondiente
    # Tambien reemplazamos "," por "."
    try:
        df["porcentaje_afectado"] = (
            df["porcentaje_afectado"]
            .astype(str)
            .str.lower()
            .str.replace("%", "")
            .str.replace(" ", "")
            .str.replace(",", ".")
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .replace(DICT_PORCENTAJE)
            .replace({"nan": np.nan})
        )
    except KeyError:
        _raise_missing_column(df, "porcentaje_afectado")

    # Convertimos a float y mostramos los cases donde salta error (que se dejan como NaN)
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

    # Warn when the values never surpass 1
    if df["porcentaje_afectado"].dropna().max() <= 1:
        logger.warning(
            "Values of 'porcentaje_afectado' never surpass 1. "
            f"Maximum: {df['porcentaje_afectado'].dropna().max()}."
            "The values are multiplied by 100."
        )
        df["porcentaje_afectado"] = df["porcentaje_afectado"] * 100
    elif 0 < df["porcentaje_afectado"].dropna().min() < 1:
        list_idx = df.query("0 < porcentaje_afectado < 1").index
        raise_value_warning(df, list_idx, "porcentaje_afectado")
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


def select_columns(df: pd.DataFrame, list_cols: list = None) -> pd.DataFrame:
    """Returns the dataframe having only the selected columns.
    If one is missing, fill it with NaNs"""
    if list_cols is None:
        list_cols = LIST_COLS_OUTPUT
    try:
        df = df[list_cols]
    except KeyError:
        cols_missing = list(set(list_cols) - set(df.columns))
        for col in cols_missing:
            df[col] = np.nan
        logger.warning(
            f"Missing columns, will be filled with NaN: {', '.join(cols_missing)}"
        )
    return df


def return_dict_provincia_to_ccaa(df: pd.DataFrame, dict_add: dict = None) -> dict:
    """Generates a dictionary where each key is a province and its value is the CCAA"""
    if dict_add is None:
        dict_add = DICT_ADD_PROVINCE
    df_ccaa = df.groupby(["comunidad_autonoma", "provincia"]).size().reset_index()

    dict_provincia_to_ccaa = dict(
        zip(df_ccaa["provincia"], df_ccaa["comunidad_autonoma"])
    )

    dict_provincia_to_ccaa.update(dict_add)
    return dict_provincia_to_ccaa


def return_dict_provincia_to_interventions(df: pd.DataFrame) -> dict:
    """Generates a dictionary where each key is a province and its value is
    the dataframe containing the limitations applied in it"""
    dict_provincia_to_ccaa = return_dict_provincia_to_ccaa(df)

    dict_provincia_to_interventions = {}

    for provincia, ccaa in dict_provincia_to_ccaa.items():
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
            dict_provincia_to_interventions.update({provincia: df_sub})

    return dict_provincia_to_interventions


def read_npi_and_build_dict(
    path_data: str = "datos_NPI",
    path_taxonomy: str = PATH_TAXONOMY,
):
    """Reads the folder containing the NPI and returns a dictionary
    {province: limitations}"""
    dict_provincia_to_interventions = {}
    for file in sorted(os.listdir(path_data)):
        logger.debug(f"...............\n{file}")
        path_file = os.path.join(path_data, file)
        try:
            df = read_npi_data(path_file)
        except IsADirectoryError:
            logger.error(
                f"File {file} could not be opened as province: not a valid file format\n...............\n"
            )
            continue
        except KeyError:
            logger.error(
                f"File {file} could not be opened as province: base sheet is missing\n...............\n"
            )
            continue
        # Filtramos las interventions relevantes
        df_filtered = filter_relevant_interventions(df, path_taxonomy=path_taxonomy)
        # Corregimos las fechas
        df_filtered = process_fecha(df_filtered)
        # Renombramos la columna unidad
        df_renamed = rename_unidad(df_filtered)
        # Formateamos "porcentaje afectado"
        df_renamed = format_porcentaje_afectado(df_renamed)
        # Pivotamos la columna "unidad" y le asignamos a cada categoría
        # su correspondiente "valor"
        df_pivot = pivot_unidad_valor(df_renamed)
        # Tomamos sólo las columnas que nos interesan
        df_output = select_columns(df_pivot)
        # Construimos el diccionario de interventions y lo guardamos
        dict_update = return_dict_provincia_to_interventions(df_output)
        dict_provincia_to_interventions.update(dict_update)
        logger.debug(f"...............\n")
    return dict_provincia_to_interventions


def main(
    path_data: str = "datos_NPI",
    path_taxonomy: str = PATH_TAXONOMY,
    path_output: str = "output/interventions",
):
    """Reads the raw data, in path_data, preprocess it and stores the results in
    path_output

    Parameters
    ----------
    path_data : str, optional
    path_taxonomy : str, optional
    path_output : str, optional

    """
    dict_provincia_to_interventions = read_npi_and_build_dict(
        path_data=path_data, path_taxonomy=path_taxonomy
    )
    store_dict_provincia_to_interventions(
        dict_provincia_to_interventions, path_output=path_output
    )


if __name__ == "__main__":
    typer.run(main)
