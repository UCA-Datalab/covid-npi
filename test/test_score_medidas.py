import pandas as pd
import pytest
from covidnpi.score.medidas import score_medidas
from covidnpi.utils.taxonomy import return_taxonomy


@pytest.fixture
def medidas() -> pd.DataFrame:
    path_medidas = "test/data/medidas.csv"
    yield pd.read_csv(path_medidas)


@pytest.fixture
def taxonomy() -> pd.DataFrame:
    path_taxonomy = "test/data/taxonomia.xlsx"
    yield return_taxonomy(path_taxonomy=path_taxonomy, path_output=None)


@pytest.fixture
def sc_medidas() -> pd.DataFrame:
    path_score = "test/data/score_medidas.csv"
    yield pd.read_csv(path_score, parse_dates=["fecha"])


def test_medidas(
    medidas: pd.DataFrame, taxonomy: pd.DataFrame, sc_medidas: pd.DataFrame
):
    sc_med = score_medidas(medidas, taxonomy, path_out_conditions=None).reset_index()
    pd.testing.assert_frame_equal(sc_med, sc_medidas, check_names=False)
