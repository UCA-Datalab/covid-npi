rm -r output/
python covidnpi/preprocess_and_score.py --path-raw datos_NPI
python covidnpi/initialize_web.py --path-config config.toml 
python covidnpi/initialize_web.py --path-config config-staging.toml 
python covidnpi/initialize_web.py --path-config config-live.toml 
