import os

import numpy as np
import pandas as pd
import typer


def read_npi_data(path_com: str) -> pd.DataFrame:
    """Read the data contained in a xlsm file"""
    col_rename = {
        "cod_con": "codigo",
        "unidad de medida": "unidad",
        "% afectado (si subprovincial; mín 25%)": "porcentaje_afectado",
        "Comunidad_autónoma": "comunidad_autonoma",
    }

    df = pd.read_excel(path_com, sheet_name="base").rename(col_rename, axis=1)

    drop_cols = [col for col in df.columns if col.startswith("Unnamed")]
    df = df.drop(drop_cols, axis=1)

    # En el caso de "p", se tiene que multiplicar por 100
    df.loc[df["unidad"] == "p", "valor"] = df.loc[df["unidad"] == "p", "valor"] * 100

    # Preprocesar texto
    for col in [
        "ambito",
        "comunidad_autonoma",
        "provincia",
        "unidad",
        "nivel_educacion",
    ]:
        try:
            df[col] = (
                df[col]
                .str.normalize("NFKD")
                .str.encode("ascii", errors="ignore")
                .str.decode("utf-8")
                .str.lower()
            )
        except AttributeError:
            print(f"{path_com} column '{col}' has all NaNs")
        except KeyError:
            print(f"{path_com} is missing '{col}'")
    # Para el codigo hacemos mas
    df["codigo"] = df["codigo"].fillna(df["cod_gen"]).replace({" ": ""})
    # Rellenamos NaNs en comunidad autonoma
    df["comunidad_autonoma"] = df["comunidad_autonoma"].fillna(
        df["comunidad_autonoma"].value_counts().index[0]
    )

    return df


def read_npi_folder(path_data: str) -> pd.DataFrame:
    list_df = []

    for file in os.listdir(path_data):
        path_file = os.path.join(path_data, file)
        df = read_npi_data(path_file)
        list_df += [df]

    df = pd.concat(list_df).reset_index(drop=True)
    return df


def gen_cod(prefix, maximo, missing=()):
    """ returns a list of the codes for a given range"""
    lista = set(range(1, maximo + 1)) - set(missing)
    return [prefix + "." + str(n) for n in lista]


def return_all_medidas():
    all_medidas = (
        gen_cod("AF", 17, [10, 11])
        + gen_cod("CD", 17)
        + gen_cod("CE", 7)
        + gen_cod("CO", 10)
        + gen_cod("ED", 4)
    )
    all_medidas += gen_cod("ON", 10, [9]) + gen_cod("LA", 3) + gen_cod("RH", 11, [8])
    all_medidas += (
        gen_cod("MV", 4) + ["RS.1", "RS.2", "RS.8", "TP.1"] + gen_cod("TR", 9)
    )
    return all_medidas


def filter_relevant_medidas(df: pd.DataFrame):
    all_medidas = return_all_medidas()
    mask_medidas = df["codigo"].isin(all_medidas)
    df_new = df[mask_medidas]
    dropped = sorted(df.loc[~mask_medidas, "codigo"].astype(str).unique())
    print("Las medidas ignoradas son:", dropped)
    return df_new


def rename_unidad(df):
    df = df.copy()

    rename = {
        "hora (en formato 24h)": "hora",
        "hora (formato 24h)": "hora",
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
    df["unidad"] = df["unidad"].replace(rename)
    return df


def format_hora(df):
    df = df.copy()
    hora = (
        df.query("codigo == 'RH.5'")["hora"].fillna(0).astype(str).str[:2].astype(int)
    )
    hora[hora <= 6] = hora[hora <= 6] + 24
    df["hora"] = hora.astype(int)
    return df


def pivot_unidad_valor(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot the column unidad so that we get one column per category"""
    # Pasamos las categorias de la columna "unidad" a columnas con valor "valor"
    df_cat = df[["unidad", "valor"]].pivot(columns="unidad", values="valor")
    df_cat = df_cat.loc[:, df_cat.columns.notnull()].reset_index(drop=True)

    df = df.join(df_cat).drop(["unidad", "valor"], axis=1)

    df = format_hora(df)
    return df


def return_dict_provincia(df: pd.DataFrame) -> dict:
    df_ccaa = df.groupby(["comunidad_autonoma", "provincia"]).size().reset_index()

    dict_provincia = dict(zip(df_ccaa["provincia"], df_ccaa["comunidad_autonoma"]))

    dict_add = {
        "palencia": "cyl",
        "soria": "cyl",
        "valencia": "comunidad_valenciana",
        "castellon": "comunidad_valenciana",
        "gran_canaria": "canarias",
        "alava": "pais_vasco",
        "guipuzcoa": "pais_vasco",
        "vizcaya": "pais_vasco",
    }

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
        dict_medidas.update({provincia: df_sub})

    return dict_medidas


def store_dict_medidas(dict_medidas, path_output: str = "../output_medidas"):
    if not os.path.exists(path_output):
        os.mkdir(path_output)

    for provincia, df_medida in dict_medidas.items():
        path_file = os.path.join(path_output, provincia.split("/")[0] + ".csv")
        df_medida = df_medida[
            [
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
        ]
        df_medida.to_csv(path_file, index=False)


def load_dict_medidas(path_medidas: str = "output_medidas"):
    dict_medidas = {}
    list_files = os.listdir(path_medidas)
    for file in list_files:
        provincia = file.rsplit(".")[0]
        path_file = os.path.join(path_medidas, file)
        df = pd.read_csv(path_file)
        dict_medidas.update({provincia: df})
    return dict_medidas


def main(path_data: str = "datos_NPI_2", path_output: str = "output_medidas"):
    # Read all files and combine them
    df = read_npi_folder(path_data)

    # Filtramos las medidas relevantes
    df_filtered = filter_relevant_medidas(df)

    # Renombramos la columna unidad
    df_renamed = rename_unidad(df_filtered)

    # Pivotamos la columna "unidad" y le asignamos a cada categoría
    # su correspondiente "valor"
    df_pivot = pivot_unidad_valor(df_renamed)

    # Construimos el diccionario de medidas y lo guardamos
    dict_medidas = return_dict_medidas(df_pivot)
    store_dict_medidas(dict_medidas, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
