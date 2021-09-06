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
      <a href="#preprocess-and-score-items">Preprocess and Score Items</a>
     </li>
     <li>
      <a href="#web-application">Web Application</a>
      <ul>
        <li><a href="#initialize-the-web-application">Initialize the Web Application</a></li>
        <li><a href="#load-data-from-mongo">Load Data from Mongo</a></li>
      </ul>
     </li>
     <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## About the project

COVID NPI

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

## Preprocess and score items

With the environment active, run the following command:

```
python covidnpi/preprocess_and_score.py
```

To see an explanation of this script, run instead:

```
python covidnpi/preprocess_and_score.py --help
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

### Load Data from Mongo

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

## Contact

David Gómez-Ullate - [dgullate](https://github.com/dgullate) -  david.gomezullate@uca.es

Project link: [https://github.com/UCA-Datalab/covid-npi](https://github.com/UCA-Datalab/covid-npi)

## Acknowledgements

* [UCA DataLab](http://datalab.uca.es/)
* [Daniel Precioso](https://www.linkedin.com/in/daniel-precioso-garcelan/)
* [Leopoldo Jesús Gutiérrez Galeano](https://www.linkedin.com/search/results/all/?keywords=leopoldo%20jes%C3%BAs%20guti%C3%A9rrez%20galeano&origin=RICH_QUERY_SUGGESTION&position=0&searchId=52369ebd-8c77-46b0-b6cb-864f095f42e2&sid=MW!)

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