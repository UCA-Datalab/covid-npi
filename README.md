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
[![LinkedIn][linkedin-shield]][linkedin-url]

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
     </li>
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

See [the README on covidnpi/web](covidnpi/web) to learn how to load the data from mongo.


## Contact

- [David Gómez-Ullate](https://github.com/dgullate), [UCADatalab](http://datalab.uca.es/)
- [Leopoldo Gutiérrez](https://github.com/leoguga), [UCADatalab](http://datalab.uca.es/)
- [Daniel Precioso](https://github.com/daniprec), [UCADatalab](http://datalab.uca.es/)
             
**Last update**: 23th june 2021