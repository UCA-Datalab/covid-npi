import os

import numpy as np
import pandas as pd
import typer
import xlrd

from covidnpi.utils.dictionaries import store_dict_medidas
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
    "Ámbito": "ambito",
    "Comunidad_Autónoma": "comunidad_autonoma",
    "cod_con": "codigo",
    "unidad de medida": "unidad",
    "% afectado (si subprovincial; mín 25%)": "porcentaje_afectado",
    "Comunidad_autónoma": "comunidad_autonoma",
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
}

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


def clean_pandas_str(series: pd.Series):
    series_cleaned = (
        series.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.lower()
        .str.replace(" ", "_")
    )
    return series_cleaned


def read_npi_data(
    path_com: str,
    col_rename: dict = DICT_COL_RENAME,
    list_col_text: list = LIST_COL_TEXT,
) -> pd.DataFrame:
    """Read the data contained in a xlsm file"""

    for sheet in LIST_BASE_SHEET:
        try:
            df = pd.read_excel(path_com, sheet_name=sheet)
            break
        except xlrd.biffh.XLRDError:
            pass
    else:
        xl = pd.ExcelFile(path_com)
        raise KeyError(f"File {path_com} does not have base sheet: {xl.sheet_names}")

    df = df.rename(col_rename, axis=1)

    drop_cols = [col for col in df.columns if col.startswith("Unnamed")]
    df = df.drop(drop_cols, axis=1)

    # En el caso de "p", se tiene que multiplicar por 100
    df.loc[df["unidad"] == "p", "valor"] = df.loc[df["unidad"] == "p", "valor"] * 100

    # Preprocesar texto
    for col in list_col_text:
        try:
            df[col] = clean_pandas_str(df[col])
        except AttributeError:
            print(f"{path_com} column '{col}' has all NaNs")
        except KeyError:
            print(f"{path_com} is missing '{col}'")
    # Para el codigo hacemos mas
    df["codigo"] = df["codigo"].fillna(df["cod_gen"]).replace({" ": ""})
    # Rellenamos NaNs en comunidad autonoma
    try:
        df["comunidad_autonoma"] = df["comunidad_autonoma"].fillna(
            df["comunidad_autonoma"].value_counts().index[0]
        )
    except KeyError:
        raise KeyError(
            f"'comunidad_autonoma' not in {path_com}: "
            f"{', '.join(df.columns.tolist())}"
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
        list_df += [df]

    df = pd.concat(list_df).reset_index(drop=True)
    return df


def gen_cod(prefix, maximo, missing=()):
    """ returns a list of the codes for a given range"""
    lista = set(range(1, maximo + 1)) - set(missing)
    return [prefix + "." + str(n) for n in lista]


def filter_relevant_medidas(df: pd.DataFrame, path_taxonomia: str = PATH_TAXONOMIA):
    all_medidas = return_all_medidas(path_taxonomia=path_taxonomia)
    mask_medidas = df["codigo"].isin(all_medidas)
    df_new = df[mask_medidas]
    dropped = sorted(df.loc[~mask_medidas, "codigo"].astype(str).unique())
    print("Las medidas ignoradas son:", dropped)
    return df_new


def rename_unidad(df, rename: dict = DICT_UNIDAD_RENAME):
    df = df.copy()

    # If any value contains the exact word, change value to word
    list_rename = set(rename.values())
    for word in list_rename:
        mask_word = df["unidad"].str.lower().str.contains(word)
        df.loc[mask_word, "unidad"] = word

    # Rename the rest
    df["unidad"] = df["unidad"].replace(rename)
    return df


def format_hora(df):
    df = df.copy()
    # Join all the columns named "hora"
    hora = (
        df.query("codigo == 'RH.5'")["hora"].fillna(0).astype(str).str[:2].astype(int)
    )
    hora[hora <= 6] = hora[hora <= 6] + 24
    df["hora"] = hora.astype(int)
    return df


def format_porcentaje_afectado(df: pd.DataFrame):
    df = df.copy()
    list_provincia = df["provincia"].unique()
    # Loop through provincias
    for provincia in list_provincia:
        mask_provincia = df["provincia"] == provincia
        porc = df.loc[mask_provincia, "porcentaje_afectado"].copy()
        # If the column is a string, convert city names to values
        try:
            porc = (
                porc.str.lower()
                .str.replace(" ", "")
                .str.replace(",", ".")
                .str.normalize("NFKD")
                .str.encode("ascii", errors="ignore")
                .str.decode("utf-8")
                .replace(DICT_PORCENTAJE)
            )
        except AttributeError:
            pass
        # If values are below 1, multiply by 100 to get percentages
        try:
            porc = porc.astype(float)
        except TypeError:
            print(f"porcentaje_afectado of {provincia} is not a float!")
        except ValueError:
            porc = pd.to_numeric(porc, errors="coerce")
            print(
                f" [Warning] String values encountered in 'porcentaje_afectado' of"
                f" {provincia}, "
                "and set to NaN"
            )
        finally:
            if porc.max() <= 1:
                porc = (porc * 100).astype(float)
        df.loc[mask_provincia, "porcentaje_afectado"] = porc
    # Round to one decimal
    df["porcentaje_afectado"] = df["porcentaje_afectado"].astype(float).round(1)
    return df


def pivot_unidad_valor(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot the column unidad so that we get one column per category"""
    # Pasamos las categorias de la columna "unidad" a columnas con valor "valor"
    df_cat = df[["unidad", "valor"]].pivot(columns="unidad", values="valor")
    df_cat = df_cat.loc[:, df_cat.columns.notnull()].reset_index(drop=True)

    df = df.join(df_cat).drop(["unidad", "valor"], axis=1)

    df = format_hora(df)
    return df


def return_dict_provincia(df: pd.DataFrame, dict_add: dict = DICT_ADD_PROVINCE) -> dict:
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
    # Read all files and combine them
    df = read_npi_folder(path_data)

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
    dict_medidas = return_dict_medidas(df_pivot)
    return dict_medidas


def main(
    path_data: str = "datos_NPI_2",
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
