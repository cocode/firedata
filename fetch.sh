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

if [[ $HOSTNAME == *"MacBook-Pro.local"  ]]
then
  echo "Don't run this on local machine! Only github."
  exit 1
fi
# Set up enough info that we can do a push back to the repository.

git config user.name "FireData Action Bot"
git config user.email "<>"

python3 -m pip install BeautifulSoup4

# Fetch the new day's fire data into the data directories.
python3 get_all_fire_data.py

# Add and commit the new data
git add data
# If there is no new data, git commit returns non-zero, so turn of checking.
set +e
git commit -m "Automatic add of new fire data"
set -e

# Build and commit the webpage.
python3 -m webpage.create_webpage_multi
cp docs/fire_ca_2021.html docs/index.html

git add docs
set +e
git commit -m "Add newly generated web page"
set -e

# Push all changes
git push

# Run code coverage and check in the percentage.
coverage run  --branch -m pytest
coverage report -m > coverage.txt
cat coverage.txt
python make_badge.py
git add code-coverage.txt
git commit code-coverage.txt
git push

echo "Done."
