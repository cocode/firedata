#set -eo pipefail
PYTHONPATH=$PWD:$PWD/webpage
echo PYTHONPATH: $PYTHONPATH
echo PWD: $PWD
python3 --version

python3 get_cal_fire_data.py
ls -al data/data_cal
ls -al data/data_us

# Add and commit the new data
git add data/data_cal
git commit -m "Automatic add of new fire data"

# Build and commit the webpage.
python3 -m webpage.create_webpage
cp webpage/fire_graphs.html docs/index.html
git add docs
git commit -m "Add newly generated web page"

# Push all changes
git push
echo "Done."
