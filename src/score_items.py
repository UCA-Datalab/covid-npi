import pandas as pd
import typer

from src.dictionaries import store_dict_scores, load_dict_scores


def compute_proportion(df: pd.DataFrame):
    return df


def score_items(df: pd.DataFrame):
    df_item = df[["fecha", "porcentaje_afectado"]].copy()

    # Deporte exterior
    df_item["DEX_afor"] = df[["AF.1", "AF.6", "AF.7"]].max(axis=0)
    return df_item


def return_dict_score_items(dict_scores: dict, verbose: bool = True) -> dict:
    dict_items = {}

    for provincia, df_sub in dict_scores.items():
        if verbose:
            print(provincia)
        df_item = score_items(df_sub)
        dict_items.update({provincia: df_item})

    return dict_items


def main(
    path_score_medidas: str = "output/score_medidas",
    path_output: str = "output/score_items",
):
    dict_scores = load_dict_scores(path_score_medidas)
    dict_items = return_dict_score_items(dict_scores)
    store_dict_scores(dict_items, path_output=path_output)


if __name__ == "__main__":
    typer.run(main)
