python covidnpi/preprocess_and_score.py --path-raw ../modelos-covid/datos_NPI_3 > log.out
python covidnpi/initialize_web.py --path-config config.toml 
python covidnpi/initialize_web.py --path-config config-staging.toml 
python covidnpi/initialize_web.py --path-config config-live.toml 
