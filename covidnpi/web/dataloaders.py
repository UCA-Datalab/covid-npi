from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo


def return_ambits_by_province(province: str, ambits: tuple, path_config: str):
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
