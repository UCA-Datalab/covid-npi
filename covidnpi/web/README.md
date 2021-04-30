# COVID NPI web application

*All the paths specified here are relative to the root folder, [covid-npi](../..)*

## First steps

To initialize the web application, you must first host a mongo server.
Make a copy of the [config file](../config.toml) and fill in the required credentials.
From now on, use that config file when running the following functions.

To store all the required data in the mongo server, run:

```
python covidnpi/initialize_web.py --path-config path-config
```

Where `path-config` leads to your copy of the config file.

## Load data from mongo

In this section we show use cases for the different functions.

To load the NPI scores of several ambits for a given province:

````python
from covidnpi.web.dataloaders import return_ambits_by_province

# Parameters to define
# province : The code of the province, in uppercase
province = "M"
# ambits : List containing the ambits
ambits = ["deporte_exterior", "cultura", "movilidad"]
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_ambits_by_province(province, ambits, path_config=path_config)
# Output dict_plot will have the following format
# {"deporte_exterior": {"x": [...], "y": [...]},
#  "cultura": {"x": [...], "y": [...]},
#  "movilidad": {"x": [...], "y": [...]}}
# where x are dates and y are floats between 0 and 1
````

To load the NPI scores of several provinces for a given ambit:

````python
from covidnpi.web.dataloaders import return_provinces_by_ambit

# Parameters to define
# ambit : The name of the ambit, in lowercase
ambit = "movilidad"
# provinces : List of provinces codes
provinces = ["M", "CA"]
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_provinces_by_ambit(ambit, provinces, path_config=path_config)
# Output dict_plot will have the following format
# {"M": {"x": [...], "y": [...]},
#  "CA": {"x": [...], "y": [...]}}
# where x are dates and y are floats between 0 and 1
````

To load the cumulative incidence in a given province:
````python
from covidnpi.web.dataloaders import return_incidence_of_province

# Parameters to define
# province : The code of the province, in uppercase
province = "M"
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_incidence_of_province(province, path_config=path_config)
# Output dict_plot will have the following format
# {"x": [...], "y": [...]}
# where x are dates and y are floats
````

To load the growth ratio in a given province:
````python
from covidnpi.web.dataloaders import return_growth_of_province

# Parameters to define
# province : The code of the province, in uppercase
province = "M"
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_growth_of_province(province, path_config=path_config)
# Output dict_plot will have the following format
# {"x": [...], "y": [...]}
# where x are dates and y are floats
````
