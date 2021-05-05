from pathlib import Path
from typing import Union

import pandas as pd
import typer

from covidnpi.utils.config import load_config
from covidnpi.utils.dictionaries import reverse_dictionary

COLS_AMBITO = [
    "fecha",
    "provincia",
    "deporte_exterior",
    "deporte_interior",
    "cultura",
    "colegios",
    "educacion_otra",
    "restauracion_exterior",
    "restauracion_interior",
    "movilidad",
    "trabajo",
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


def add_province_code(df: pd.DataFrame, path_config: str = "covidnpi/config.toml"):
    province_to_code = load_config(path_config, "provincia_to_code")
    code_to_province = load_config(path_config, "code_to_provincia")
    postal_to_code = load_config(path_config, "postal_to_code")
    code_to_postal = reverse_dictionary(postal_to_code)
    code = df["provincia"].map(province_to_code)
    # Replace province name and add code
    df["provincia"] = code.map(code_to_province)
    df = df.insert(loc=1, column="cod_prov", value=code.map(code_to_postal))
    return df


def combine_csv_ambito(
    path_data: str = "output/score_ambito", path_output: str = "npi_stringency.csv"
) -> pd.DataFrame:
    df = combine_csv(path_data, "provincia")
    # Tomar las columnas relevantes y ordenar por fecha
    df = df[COLS_AMBITO].sort_values(["fecha", "provincia"])
    df = add_province_code(df)
    df.to_csv(path_output, index=False)


if __name__ == "__main__":
    typer.run(combine_csv_ambito)
