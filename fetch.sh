set -euo pipefail
date
PYTHONPATH=$PWD:$PWD/webpage
echo PYTHONPATH: $PYTHONPATH
echo PWD: $PWD
python3 --version

git config user.name "FireData Action Bot"
git config user.email "<>"

python3 -m pip install BeautifulSoup4

python3 get_all_fire_data.py
ls -al data/data_cal
ls -al data/data_us
ls -al data/data_wa

# Add and commit the new data
git add data
git commit -m "Automatic add of new fire data"

# Build and commit the webpage.
python3 -m webpage.create_webpage
cp webpage/fire_graphs.html docs/index.html
git add docs
git commit -m "Add newly generated web page"

# Push all changes
git push
echo "Done."
