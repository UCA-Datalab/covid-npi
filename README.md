<!-- README template: https://github.com/othneildrew/Best-README-Template -->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/UCA-Datalab">
    <img src="images/logo.png" alt="Logo" width="400" height="80">
  </a>

  <h3 align="center">COVID NPI</h3>
</p>


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#create-the-environment">Create the Environment</a></li>
      </ul>
    </li>
    <li>
      <a href="#data">Data</a>
      <ul>
        <li><a href="#non-pharmaceutical-interventions">Non-Pharmaceutical Interventions</a></li>
        <li><a href="#taxonomy">Taxonomy</a></li>
      </ul>
    </li>
    <li>
      <a href="#preprocess-and-score-items">Preprocess and Score Items</a>
     </li>
     <li>
      <a href="#web-application">Web Application</a>
      <ul>
        <li><a href="#initialize-the-web-application">Initialize the Web Application</a></li>
        <li><a href="#load-data-from-mongo">Load Data from Mongo</a></li>
      </ul>
     </li>
     <li><a href="#glossary">Glossary</a></li>
     <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## About the project

We quantify the restriction level of non-pharmaceutical interventions during COVID, in Spain.

## Getting started
### Create the environment

To create the environment using Conda:

  1. Install miniconda
     
     ```
     curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | bash
     ```

     Say yes to everything and accept default locations. Refresh bash shell with `bash -l`

  2. Update conda
     
      ```
      conda update -n base -c defaults conda
      ```

  3. Clone this repository and cd into the folder

  4. Create and activate conda environment (removing previously existing env of the same name)
     
       ```
       conda remove --name covid-npi --all
       conda env create -f environment.yml --force
       conda activate covid-npi

  5. (Optional) Install the Jupyter kernel
       ```
       pip install --user ipykernel
       python -m ipykernel install --user --name=covid-npi
       ```

## Data

The data required to run this module must be provided by the user, and must follow the format specified below.

### Non-Pharmaceutical Interventions

Non-Pharmaceutical Interventions (NPI) files should be located in a folder named [datos_NPI](./datos_NPI) at root level. This folder contains one file per region (autonomous community), in xlsm or xlsx format.

The name of the files does not matter, but it is important that they have a sheet labelled `base` inside. Other valid names for the sheet are `base-regional-provincias`, `BASE` or `Base`. Files without this sheet will raise the following error when trying to be processed:

```
[ERROR] File could not be opened as province: base sheet is missing
```

The `base` sheet describes one **intervention (NPI)** per row. Interventions apply to a specific field of activity (such as "culture" or "mobility") and may affect all the region or only part of it, during a certain period of time. The `base` sheet should contain the following columns:

- `ambito` can take the values "autonómico" when the intervention affects the whole autonomous community, "provincial" when it applies to a province (see `provincia`), or "subprovincial" when it only affects part of a province (see `porcentaje_afectado`).
- `comunidad_autonoma` contains the name of the autonomous community. Must be the same in the whole file.
- `provincia` contains the name of the province affected by the intervention, when `ambito` is "provincial" or "subprovincial".
- `fecha_publicacion` contains the date of publication of the intervention. Format is "MM/DD/YY".
- `fecha_inicio` contains the date of start of the intervention. Format is "MM/DD/YY".
- `fecha_fin` contains the date of end of the intervention. Format is "MM/DD/YY".
- `intervention_concreta` contains the description of the intervention. Not used by this module.
- `codigo` or `cod_con` contains the specific code of the intervention.
- `intervention_generica` is not used by this module.
- `cod_gen` is not used by this module.
- `unidad` is only used by certain interventions, when certain value needs to be specified. This column contains the units of that value. Examples are "hora", "personas" and "porcentaje".
- `valor` comes in conjunction with `unidad`. Contains the value.
- `porcentaje_afectado` contains the percentage (over 100) affected by the intervention, when `ambito` is "subprovincial".
- `nivel_educacion`

### Taxonomy

Taxonomy is a xslx file, and must be placed in the same [datos_NPI](./datos_NPI) folder as the data above. Each sheet in the taxonomy corresponds to a specific field of activity, such as "commerce", "education" or "outside sport". These sheets have the following columns:

- `Código intervention concreta` contains the specific code of the intervention (NP). Related to the column `codigo` of the NPI files.
- `Media concreta` contains the description of the NPI. Not used by this module.
- `Nombre item` contains the name of the item which the interventions are associated to.
- `Construcción del item` contains the rules that describe how to compute the score of the item from the scores of the NPI associated to it.
- `Ponderación del item` contains the weight (between 0 and 1) given to the item. It is used to compute the field score.
- `Criterio` contains the rules that describe how to score the NPI.

## Preprocess and Score Items

With the environment active, run the following command:

```
python covidnpi/store_stringency_scores.py
```

To see an explanation of this script, run instead:

```
python covidnpi/store_stringency_scores.py --help
```

## Web Application

Our web service is hosted at [http://npispain.clapton.uca.es/#/home](http://npispain.clapton.uca.es/#/home)

If you want to host your own web application, follow the instructions in this section. Else, you can skip to [Contact](#contact) section.

### Initialize the Web Application

To initialize the web application, you must first host a mongo server.
Make a copy of the [config file](covidnpi/config.toml) and fill in the required credentials.
From now on, use that config file when running the following functions.

To store all the required data in the mongo server, run:

```
python covidnpi/initialize_web.py --path-config path-config
```

Where `path-config` leads to your copy of the config file.

### Web API configuration

The Web API is in charge of sending the project data from the backend hosted on Zappa, to the web application hosted on Clapton (served using Apache2).


The Web API is composed of the Mongo service and a Flask app that sends the data from Zappa to Clapton, the entire orchestation is managed from `/DATA2/ucadatalab_group/leo/npi-spain`.  Here you can find 6 directories: 3 for mongo, Flask and the venv of the live (production) version, and 3 for the stagging version:

- mongo-live          
- npi-spain-api-live 
- venv_npi-spain-api-live          

- npi-spain-api-staging
- mongo-staging    
- venv_npi-spain-api-staging


There is a system daemon to run the Flask app for the live version , that can be executed using `sudo systemctl start npi-spain.service`, this will run the flask app on Zappa using port 5010. 

The configuration of this daemon can be found on `/etc/systemd/system/npi-spain.service`.

\* systemctl command can also be used to check the status of the daemon, to stop it, or reboot it, for more info check: https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units 




### Load Data from Mongo

In this section we show use cases for the different functions.

To load the NPI scores of several fields for a given province:

````python
from covidnpi.web.dataloaders import return_fields_by_province

# Parameters to define
# province : The code of the province, in uppercase
province = "M"
# fields : List containing the fields
fields = ["deporte_exterior", "cultura", "movilidad"]
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_fields_by_province(province, fields, path_config=path_config)
# Output dict_plot will have the following format
# {"deporte_exterior": {"x": [...], "y": [...]},
#  "cultura": {"x": [...], "y": [...]},
#  "movilidad": {"x": [...], "y": [...]}}
# where x are dates and y are floats between 0 and 1
````

To load the NPI scores of several provinces for a given field:

````python
from covidnpi.web.dataloaders import return_provinces_by_ambit

# Parameters to define
# field : The name of the field, in lowercase
field = "movilidad"
# provinces : List of provinces codes
provinces = ["M", "CA"]
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_provinces_by_ambit(field, provinces, path_config=path_config)
# Output dict_plot will have the following format
# {"M": {"x": [...], "y": [...]},
#  "CA": {"x": [...], "y": [...]}}
# where x are dates and y are floats between 0 and 1
````

To load the cumulative cases in a given province:
````python
from covidnpi.web.dataloaders import return_cases_of_province

# Parameters to define
# province : The code of the province, in uppercase
province = "M"
# path_config : Path to your config file
path_config = "config.toml"

dict_plot = return_cases_of_province(province, path_config=path_config)
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

## Glossary

- **Field (of activity):** Specific group of activities where NPI are applied. Examples are "commerce", "education" and "outside sports".
- **Field Score:** Represents how restricted are the activities related to that field, from 0 (no restriction) to 1 (activity is not allowed). Field score is computed by weighting the scores of the items related to that field. The weights of each item are given by the taxonomy.
- **Intervention:** see "Non-Pharmaceutical Intervention".
- **Item:** An item is part of an field of activity. It relates to a specific topic within the field. For instance, the field "culture" has the items "museum" and "cinema" among others.
- **Item Score:** Represents how restricted are the activities related to that item, from 0 (no restriction) to 1 (activity is not allowed). Item score is computed from the scores of the NPI related to that item, following the rules described in the taxonomy.
- **Non-Pharmaceutical Intervention:** Interventions are restrictions over a specific field of activity (such as "culture" or "mobility") and may affect all the region or only part of it, during a certain period of time.
- **NPI:** Initials of "Non-Pharmaceutical Intervention".
- **NPI Score:** Severity of the NPI, how restrictive the intervention is. It has four levels: none (score of 0), low (0.2), medium (0.5) and high (score of 1).
- **Score:** Level of restriction impossed by a NPI or a group of NPI, from 0 to 1. Scores are computed following the rules given by the taxonomy. NPI scores are used to compute item scores, while item scores are required to compute field scores.
- **Taxonomy:** File that contains the rules to compute the sevirity of each NPI, and the score of items and fields of activity.

## Contact

David Gómez-Ullate - [dgullate](https://github.com/dgullate) -  david.gomezullate@uca.es

Project link: [https://github.com/UCA-Datalab/covid-npi](https://github.com/UCA-Datalab/covid-npi)

## Acknowledgements

* [UCA DataLab](http://datalab.uca.es/)
* [Daniel Precioso](https://daniprec.github.io/)
* [Leopoldo Jesús Gutiérrez Galeano](https://www.linkedin.com/search/results/all/?keywords=leopoldo%20jes%C3%BAs%20guti%C3%A9rrez%20galeano&origin=RICH_QUERY_SUGGESTION&position=0&searchId=52369ebd-8c77-46b0-b6cb-864f095f42e2&sid=MW!)
* [Francisco Amor Roldán](https://www.linkedin.com/in/francisco-amor-97b27820b/)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/UCA-Datalab/covid-npi.svg?style=for-the-badge
[contributors-url]: https://github.com/UCA-Datalab/covid-npi/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/UCA-Datalab/covid-npi.svg?style=for-the-badge
[forks-url]: https://github.com/UCA-Datalab/covid-npi/network/members
[stars-shield]: https://img.shields.io/github/stars/UCA-Datalab/covid-npi.svg?style=for-the-badge
[stars-url]: https://github.com/UCA-Datalab/covid-npi/stargazers
[issues-shield]: https://img.shields.io/github/issues/UCA-Datalab/covid-npi.svg?style=for-the-badge
[issues-url]: https://github.com/UCA-Datalab/covid-npi/issues