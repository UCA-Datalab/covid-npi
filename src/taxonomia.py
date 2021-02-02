import pandas as pd

PATH_TAXONOMIA = "datos_NPI/Taxonomía_23012021.xlsx"


def return_all_medidas(
    path_taxonomia=PATH_TAXONOMIA,
        verbose=False
):
    """Returns a list of the relevant medidas"""

    xl = pd.ExcelFile(path_taxonomia)

    list_sheet = xl.sheet_names
    list_codigos = []

    for sheet in list_sheet:
        try:
            df = xl.parse(sheet)
            list_codigos += df["Código medida concreta"].unique().tolist()
        except KeyError:
            if verbose:
                print(f"Sheet '{sheet}' omitted")

    return sorted(set(list_codigos))
