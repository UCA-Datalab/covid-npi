import pandas as pd


def mask_codigo(df: pd.DataFrame, codigo: str):
    df_sub = df.query(f"codigo.str.startswith('{codigo}')")
    return df_sub


def score_item(
    df: pd.DataFrame,
    bajo: str = "codigo == 'None'",
    medio: str = "codigo == 'None'",
    alto: str = "codigo == 'None'",
    method: str = "max",
):

    # Copy the df and add the item column
    df = df.copy()
    df["item"] = 0

    # Apply masks
    mask_bajo = df.query(bajo).index
    mask_medio = df.query(medio).index
    mask_alto = df.query(alto).index

    # Change values accordingly
    df.loc[mask_bajo, "item"] = 0.3
    df.loc[mask_medio, "item"] = 0.6
    df.loc[mask_alto, "item"] = 1

    # Compute the score of the item
    if method == "max":
        return df.groupby(["provincia", "fecha"])["item"].max()
    elif method == "mean":
        item = df.groupby(["provincia", "fecha"])["item"].mean()
        # Cuando una de las condiciones es 0, no se hace la media
        vmin = df.groupby(["provincia", "fecha"])["item"].min()
        vmax = df.groupby(["provincia", "fecha"])["item"].max()
        item[vmin == 0] = vmax[vmin == 0]
        return item
    else:
        raise ValueError(f"Method {method} not valid")


def score_ceremonias(df: pd.DataFrame) -> pd.DataFrame:
    # Cogemos las medidas relevantes
    df_sub = mask_codigo(df, "CE")

    # Score items
    item1 = score_item(
        df_sub,
        alto="codigo == 'CE.1'",
        medio="codigo == 'CE.2' & porcentaje <= 35",
        bajo="codigo == 'CE.2' & porcentaje > 35",
    )
    item2 = score_item(df_sub, alto="codigo == 'CE.1' | codigo == 'CE.7'")
    item3 = score_item(
        df_sub,
        medio="(codigo == 'CE.3' | codigo == 'CE.4') "
        "& (porcentaje <= 35 | personas <= 10)",
        bajo="(codigo == 'CE.3' | codigo == 'CE.4') "
        "& (porcentaje > 35 | personas > 10)",
        method="mean",
    )
    item4 = score_item(
        df_sub,
        medio="(codigo == 'CE.5' | codigo == 'CE.6') "
        "& (porcentaje <= 35 | personas <= 10)",
        bajo="(codigo == 'CE.5' | codigo == 'CE.6') "
        "& (porcentaje > 35 | personas > 10)",
        method="mean",
    )

    scores = pd.DataFrame(
        {"item1": item1, "item2": item2, "item3": item3, "item4": item4}
    ).fillna(0)
    scores["total"] = scores.sum(axis=1)
    return scores.reset_index()


def score_comercio(df: pd.DataFrame) -> pd.DataFrame:
    # Cogemos las medidas relevantes
    df_sub = mask_codigo(df, "CO")

    # Score items
    item1 = score_item(
        df_sub,
        alto="codigo == 'CO.1'",
        medio="codigo == 'CO.8' & porcentaje <= 35",
        bajo="codigo == 'CO.8' & porcentaje > 35",
    )
    item2 = score_item(df_sub, alto="codigo == 'CO.1'", bajo="codigo == 'CO.7'")
    item3 = score_item(df_sub, alto="codigo == 'CO.1'", bajo="codigo == 'CO.2'")
    item4 = score_item(df_sub, alto="codigo == 'CO.1'", bajo="codigo == 'CO.3'")
    item5 = score_item(
        df_sub,
        alto="codigo == 'CO.4'",
        medio="codigo == 'CO.9' & porcentaje <= 35",
        bajo="codigo == 'CO.9' & porcentaje > 35",
    )
    item6 = score_item(df_sub, alto="codigo == 'CO.4' | codigo == 'CO.5'")
    item7 = score_item(
        df_sub,
        alto="codigo == 'CO.6'",
        medio="codigo == 'CO.10' & porcentaje <= 35",
        bajo="codigo == 'CO.10' & porcentaje > 35",
    )

    scores = pd.DataFrame(
        {
            "item1": item1,
            "item2": item2,
            "item3": item3,
            "item4": item4,
            "item5": item5,
            "item6": item6,
            "item7": item7,
        }
    ).fillna(0)
    scores["total"] = (
        item1 + item2 + 0.5 * item3 + 0.2 * item4 + item5 + 0.5 * item6 + 0.8 * item7
    )

    return scores.reset_index()


def score_deporte_exterior(df: pd.DataFrame) -> pd.DataFrame:
    # Cogemos las medidas relevantes
    df_sub = mask_codigo(df, "AF")

    # Score items
    item1 = score_item(
        df_sub,
        alto="codigo == 'AF.1'",
        medio="(codigo == 'AF.6' & (porcentaje <= 35 | personas <= 6)) "
        "| (codigo == 'AF.7' & personas <= 6)",
        bajo="(codigo == 'AF.6' & (porcentaje > 35 | personas > 6 | personas == @nan)) "
        "| (codigo == 'AF.7' & (personas > 6 | personas == @nan))",
    )
    item2 = score_item(
        df_sub,
        alto="codigo == 'AF.4'",
        medio="codigo == 'AF.17' & (personas <= 6 | personas == @nan)",
        bajo="codigo == 'AF.17' & personas > 6",
    )
    item3 = score_item(
        df_sub,
        alto="codigo == 'AF.3' | codigo == 'AF.13'",
        medio="codigo == 'AF.15' & porcentaje <= 35",
        bajo="codigo == 'AF.15' & porcentaje > 35",
    )

    scores = pd.DataFrame({"item1": item1, "item2": item2, "item3": item3}).fillna(0)
    scores["total"] = item1 + 0.6 * item2 + item3

    return scores.reset_index()


def score_educacion(df: pd.DataFrame) -> pd.DataFrame:
    # Cogemos las medidas relevantes
    df_sub = mask_codigo(df, "ED")

    scores = {}

    # Hay que aplicar las medidas para los diferentes niveles educativos
    niveles = df_sub["nivel_educacion"].dropna().unique()
    for n in niveles:
        df_niv = df_sub.query(f"nivel_educacion == '{n}'")
        item1 = score_item(
            df_niv, alto="codigo == 'ED.1'", medio="codigo == 'ED.2' | codigo == 'ED.5'"
        )
        scores.update({"item1" + n: item1})
    item2 = score_item(
        df_sub,
        alto="codigo == 'ED.3'",
        medio="codigo == 'ED.4' & porcentaje <= 35",
        bajo="codigo == 'ED.4' & porcentaje > 35",
    )
    scores.update({"item2": item2})
    scores = pd.DataFrame(scores).fillna(0)
    scores["total"] = scores[["item1" + n for n in niveles]].sum(axis=1) + item2 * 0.2

    return scores.reset_index()


def score_trabajo(df: pd.DataFrame) -> pd.DataFrame:
    # Cogemos las medidas relevantes
    df_sub = mask_codigo(df, "TR")

    # Score items
    item1 = score_item(
        df_sub,
        alto="codigo == 'TR.1'",
        medio="codigo == 'TR.2'",
        bajo="codigo == 'TR.3'",
    )

    # TODO: item 2
    scores = pd.DataFrame({"item1": item1})

    return scores.reset_index()
