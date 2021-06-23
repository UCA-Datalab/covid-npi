import pandas as pd
import pytest
from covidnpi.score.score_medidas import score_medidas
from covidnpi.utils.taxonomia import return_taxonomia


@pytest.fixture
def medidas() -> pd.DataFrame:
    path_medidas = "test/data/medidas.csv"
    yield pd.read_csv(path_medidas)


@pytest.fixture
def taxonomia() -> pd.DataFrame:
    path_taxonomia = "test/data/taxonomia.xlsx"
    yield return_taxonomia(path_taxonomia=path_taxonomia, path_output=None)


@pytest.fixture
def sc_medidas() -> pd.DataFrame:
    path_score = "test/data/score_medidas.csv"
    yield pd.read_csv(path_score, parse_dates=["fecha"])


def test_score_medidas(
    medidas: pd.DataFrame, taxonomia: pd.DataFrame, sc_medidas: pd.DataFrame
):
    sc_med = score_medidas(medidas, taxonomia, path_out_conditions=None).reset_index()
    pd.testing.assert_frame_equal(sc_med, sc_medidas, check_names=False)
