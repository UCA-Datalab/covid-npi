import pandas as pd
import pytest
from covidnpi.score.interventions import score_interventions
from covidnpi.utils.taxonomy import return_taxonomy


@pytest.fixture
def interventions() -> pd.DataFrame:
    path_interventions = "test/data/interventions.csv"
    yield pd.read_csv(path_interventions)


@pytest.fixture
def taxonomy() -> pd.DataFrame:
    path_taxonomy = "test/data/taxonomy.xlsx"
    yield return_taxonomy(path_taxonomy=path_taxonomy, path_output=None)


@pytest.fixture
def sc_interventions() -> pd.DataFrame:
    path_score = "test/data/score_interventions.csv"
    yield pd.read_csv(path_score, parse_dates=["fecha"])


def test_interventions(
    interventions: pd.DataFrame, taxonomy: pd.DataFrame, sc_interventions: pd.DataFrame
):
    sc_med = score_interventions(
        interventions, taxonomy, path_out_conditions=None
    ).reset_index()
    pd.testing.assert_frame_equal(sc_med, sc_interventions, check_names=False)
