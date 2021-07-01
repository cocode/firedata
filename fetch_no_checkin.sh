set -euo pipefail
# Time of run (GMT)
date
# Time run, California time.
TZ=America/Los_Angeles date
PYTHONPATH=$PWD:$PWD/webpage
# Dump environment info, for troubleshooting.
echo PYTHONPATH: $PYTHONPATH
echo PWD: $PWD
python3 --version


python3 -m pip install BeautifulSoup4

# Fetch the new day's fire data into the data directories.
python3 get_all_fire_data.py

# Add and commit the new data

# Build and commit the webpage.
python3 -m webpage.create_webpage_multi
cp docs/fire_ca_2021.html docs/index.html


echo "Done."
