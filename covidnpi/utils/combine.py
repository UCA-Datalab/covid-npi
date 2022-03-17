from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import typer
from covidnpi.utils.regions import (
    ISOPROV_TO_POSTAL,
    ISOPROV_TO_PROVINCIA,
    ISLA_TO_PROVINCIA,
    PROVINCIA_LOWER_TO_ISOPROV,
)

COLS_AMBITO = [
    "fecha",
    "provincia",
    "deporte_exterior",
    "deporte_interior",
    "cultura",
    # "colegios",
    # "educacion_otra",
    "restauracion_exterior",
    "restauracion_interior",
    "movilidad",
    # "trabajo",
]


def combine_csv(path: Union[Path, str], colname: str) -> pd.DataFrame:
    """Combina multiples CSVs en un único DataFrame, creando una columna `colname`
    con el nombre del fichero al que pertenece cada fila (sin la extensión)

    Parameters
    ----------
    path : Path or str
        Directorio donde se encuentran los ficheros CSV
    colname : str
        Nombre de la columna que contiene el nombre del fichero

    Returns
    -------
    pd.DataFrame
        DataFrame con el contenido de todos los CSVs
    """
    df_dict = {fin.stem: pd.read_csv(fin) for fin in Path(path).glob("*.csv")}
    return pd.concat(df_dict, names=[colname]).reset_index().drop(columns="level_1")


def add_unidad_territorial(df: pd.DataFrame) -> pd.DataFrame:
    # Check for islands
    unidad = df["provincia"].copy()
    province = df["provincia"].replace(ISLA_TO_PROVINCIA)
    # Create unidad_territorial column, that contains the islands
    df.insert(loc=2, column="unidad_territorial", value=unidad)
    df.loc[unidad == province, "unidad_territorial"] = np.nan
    df["provincia"] = province
    return df


def add_province_code(df: pd.DataFrame) -> pd.DataFrame:
    # Get codes
    code = df["provincia"].map(PROVINCIA_LOWER_TO_ISOPROV)
    # Replace province name and add code
    df["provincia"] = code.map(ISOPROV_TO_PROVINCIA)
    df.insert(loc=1, column="cod_prov", value=code.map(ISOPROV_TO_POSTAL))
    return df


def add_ccaa(df: pd.DataFrame, path_ccaa: str = "data/CCAA.csv") -> pd.DataFrame:
    ccaa = pd.read_csv(path_ccaa, dtype={"Codigo": str, "Cod_CCAA": str})
    code_to_ccaa = dict(zip(ccaa["Codigo"], ccaa["CCAA"]))
    df.insert(loc=1, column="ccaa", value=df["cod_prov"].map(code_to_ccaa))
    code_to_codccaa = dict(zip(ccaa["Codigo"], ccaa["Cod_CCAA"]))
    df.insert(loc=2, column="cod_ccaa", value=df["cod_prov"].map(code_to_codccaa))
    return df


def combine_csv_field(
    path_data: str = "output/score_field", path_output: str = "npi_stringency.csv"
) -> pd.DataFrame:
    df = combine_csv(path_data, "provincia")
    # Tomar las columnas relevantes y ordenar por fecha
    df = df[COLS_AMBITO].sort_values(["fecha", "provincia"])
    df = df.pipe(add_unidad_territorial).pipe(add_province_code).pipe(add_ccaa)
    df.to_csv(path_output, index=False)


if __name__ == "__main__":
    typer.run(combine_csv_field)
