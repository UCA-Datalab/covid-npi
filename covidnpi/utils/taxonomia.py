import pandas as pd

PATH_TAXONOMIA = "datos_NPI/Taxonomía_07022021.xlsx"


def read_taxonomia(path_taxonomia: str = PATH_TAXONOMIA) -> pd.DataFrame:
    xl = pd.ExcelFile(path_taxonomia)

    list_sheet = xl.sheet_names
    list_df = []

    col_rename = {
        "Código medida concreta": "codigo",
        "Medida concreta": "medida",
        "Ponderación del item": "ponderacion",
        "Nombre item": "nombre",
        "Nombre ítem": "nombre2",
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
        # Add ambito
        df["ambito"] = sheet
        list_df += [df]

    df = pd.concat(list_df).reset_index(drop=True)

    # If "nombre2" columns exists, fill NaNs of "nombre" with it
    try:
        df["nombre"] = df["nombre"].fillna(df["nombre2"])
        df.drop(["nombre2"], axis=1, inplace=True)
    except KeyError:
        pass

    return df


def return_all_medidas(path_taxonomia: str = PATH_TAXONOMIA):
    """Returns a list of the relevant medidas"""

    df = read_taxonomia(path_taxonomia=path_taxonomia)

    list_codigos = df["codigo"].unique().tolist()

    for codigo in ["ED.1", "ED.2", "ED.5"]:
        if codigo in list_codigos:
            list_codigos.remove(codigo)
            for niv in ["I", "P", "S", "B", "U"]:
                list_codigos += [codigo + niv]

    return sorted(list_codigos)


def classify_criteria(taxonomia: pd.DataFrame):
    """Parses "Criterio" column into three categories:
    "alto", "medio", "bajo"
    """
    criterio = (
        taxonomia["Criterio"]
        .str.replace("\n", "")
        .str.lower()
        .str.replace(" ", "")
        .str.split("si")
    )

    classified = []
    for i, row in enumerate(criterio):
        c = [""] * 3
        for s in row:
            if "alto" in s:
                c[0] = s.replace("alto", "")
            elif "medio" in s:
                c[1] = s.replace("medio", "")
            elif "bajo" in s:
                c[2] = s.replace("bajo", "")
        classified += [c]

    classified = pd.DataFrame(classified, columns=["alto", "medio", "bajo"])
    for col in classified.columns:
        classified[col] = (
            classified[col]
            .str.replace("[;=]$", "", regex=True)
            .str.replace("[;=]$", "", regex=True)
            .str.replace("pormesa$", "", regex=True)
        )

    return classified


def return_taxonomia(path_taxonomia: str = PATH_TAXONOMIA):
    taxonomia = read_taxonomia(path_taxonomia)
    criterio = classify_criteria(taxonomia)
    taxonomia = pd.merge(taxonomia, criterio, left_index=True, right_index=True)
    return taxonomia


def return_item_ponderacion(
    path_taxonomia: str = PATH_TAXONOMIA,
) -> pd.DataFrame:
    taxonomia = read_taxonomia(path_taxonomia)
    # Fill missing names with "variable" + item count
    mask_nan = taxonomia["nombre"].isna()

    taxonomia.loc[mask_nan, "nombre"] = (
        taxonomia.loc[mask_nan, "variable"].str[:3].str.upper()
        + "_"
        + taxonomia.loc[mask_nan, "item"].astype(str)
    )
    # Extract the ponderation of each item
    ponderacion = (
        taxonomia[["ambito", "nombre", "ponderacion"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return ponderacion
