rm -r output/
rm output.zip
python covidnpi/store_stringency_scores.py --path-raw datos_NPI
python covidnpi/store_incidence_rates.py
python covidnpi/initialize_web.py --path-config config.toml 
python covidnpi/initialize_web.py --path-config config-staging.toml 
python covidnpi/initialize_web.py --path-config config-live.toml 
zip -r output.zip output/