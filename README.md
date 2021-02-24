# COVID NPI

## Set up
### Create the environment using Conda

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

## Web

See [the README on covidnpi/web](covidnpi/web) to learn how to load the data from mongo.


## Credits

**Authors:**
- [David Gómez-Ullate](https://github.com/dgullate), [UCADatalab](http://datalab.uca.es/)
- [Leopoldo Gutiérrez](https://github.com/leoguga), [UCADatalab](http://datalab.uca.es/)
- [Daniel Precioso](https://github.com/daniprec), [UCADatalab](http://datalab.uca.es/)
             
**Last update**: 24th february 2021