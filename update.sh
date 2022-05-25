rm -r output/
rm output.zip
python covidnpi/store_stringency_scores.py --path-raw datos_NPI
python covidnpi/store_cases.py
python covidnpi/initialize_web.py --path-config config.toml --free-memory
python covidnpi/initialize_web.py --path-config config-staging.toml --free-memory
python covidnpi/initialize_web.py --path-config config-live.toml --free-memory
zip -r output.zip output/
zip -r output/score_field.zip output/score_field