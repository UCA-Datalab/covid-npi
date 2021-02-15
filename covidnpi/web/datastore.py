import os

import pandas as pd

from covidnpi.utils.taxonomia import return_taxonomia
from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo

from datetime import date


def store_outputs_in_mongo(
    path_output: str = "output/score_ambito",
    path_taxonomia="datos_NPI/Taxonomía_07022021.xlsx",
    path_config: str = "covidnpi/config.toml",
):
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)

    taxonomia = return_taxonomia(path_taxonomia=path_taxonomia)
    list_ambito = taxonomia["ambito"].unique().tolist()

    list_dates = pd.date_range(cfg_mongo["date_min"], date.today())
    mongo.insert_new_dict(
        "fechas", {"x": [d.strftime("%d-%m-%Y") for d in list_dates]}
    )

    for file in os.listdir(path_output):
        path_file = os.path.join(path_output, file)
        df = pd.read_csv(path_file, index_col="fecha")
        df = df.reindex(list_dates, fill_value=0)
        provincia = file.split(".")[0]
        dict_provincia = {}
        for ambito in list_ambito:
            series = df[ambito].values.tolist()
            dict_provincia.update({ambito: series})
        mongo.insert_new_dict("score", {provincia: dict_provincia})
