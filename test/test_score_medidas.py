import pandas as pd

from covidnpi.score.score_medidas import medidas_to_score
from covidnpi.utils.taxonomia import return_taxonomia


def test_score_medidas(
    path_medidas: str = "test/data/medidas.csv",
    path_taxonomia: str = "test/data/taxonomia.xlsx",
    path_tax_out: str = "test/data/taxonomia.csv",
    path_score: str = "test/data/score_medidas.csv",
):
    taxonomia = return_taxonomia(
        path_taxonomia=path_taxonomia, path_output=path_tax_out
    )
    med = pd.read_csv(path_medidas)
    sc_med = medidas_to_score(med, taxonomia)
    sc_med.to_csv(path_score)
