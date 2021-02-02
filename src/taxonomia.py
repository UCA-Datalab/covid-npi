import pandas as pd

PATH_TAXONOMIA = "../../modelos-covid/datos_NPI/Taxonomía_23012021.xlsx"


def read_taxonomia(path_taxonomia=PATH_TAXONOMIA):
    xl = pd.ExcelFile(path_taxonomia)

    list_sheet = xl.sheet_names
    list_df = []

    col_rename = {
        "Código medida concreta": "codigo",
        "Medida concreta": "medida",
        "Ponderación del item": "ponderacion",
    }

    for sheet in list_sheet:
        df = xl.parse(sheet).rename(col_rename, axis=1)
        # Creamos las columnas "variable", que indica el ambito donde se aplican las
        # medidas, e "item", que agrupa las medidas por items
        df["variable"] = sheet
        df["item"] = 1
        try:
            # Si una fila no tiene informacion en "ponderacion" es porque pertenece al
            # mismo item que la anterior fila
            df.loc[df["ponderacion"].isna(), "item"] = 0
            df["item"] = df["item"].cumsum()
            df.fillna(method="ffill", inplace=True)
        except KeyError:
            continue
        list_df += [df]

    df = pd.concat(list_df).reset_index(drop=True)

    return df


def return_all_medidas(path_taxonomia=PATH_TAXONOMIA):
    """Returns a list of the relevant medidas"""

    df = read_taxonomia(path_taxonomia=path_taxonomia)

    list_codigos = df["codigo"].unique().tolist()

    return list_codigos
