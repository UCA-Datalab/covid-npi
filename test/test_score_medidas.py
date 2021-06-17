import pandas as pd

from covidnpi.score.score_medidas import score_medidas
from covidnpi.utils.taxonomia import return_taxonomia


def test_score_medidas(
    path_medidas: str = "test/data/medidas.csv",
    path_taxonomia: str = "test/data/taxonomia.xlsx",
):
    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia, path_output=None)
    med = pd.read_csv(path_medidas)
    sc_med = score_medidas(med, taxonomia, path_out_conditions=None)
