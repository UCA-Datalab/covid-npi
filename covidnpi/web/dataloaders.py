from covidnpi.utils.config import load_config
from covidnpi.web.mongo import load_mongo


def return_ambits_by_province(
    province: str, ambits: tuple, path_config: str = "covidnpi/config.toml"
):
    cfg_mongo = load_config(path_config, key="mongo")
    mongo = load_mongo(cfg_mongo)
    col = mongo.get_col("scores")

    x = col.find_one({"provincia": "fechas"})["x"]
    dict_provincia = col.find_one({"provincia": province})

    dict_plot = {}

    for ambit in ambits:
        y = dict_provincia[ambit]
        dict_plot.update({ambit: {"x": x, "y": y}})

    return dict_plot


if __name__ == "__main__":
    dict_plot = return_ambits_by_province(
        "madrid", ("comercio", "movilidad"), path_config="config.toml"
    )
    print(dict_plot)
