PYTHONPATH=$PWD:$PWD/webpage
echo $PYTHONPATH
echo Add other actions to build,
echo test, and deploy your project.
echo $PWD
python3 --version
ls -al
ls -al data
ls -al data/data_cal
python3 get_cal_fire_data.py
ls -al data/data_cal
git add data/data_cal
git commit -m "Automatic add of new fire data"
git add docs
git commit -m "Add newly generated web page"
git push
python3 -m webpage.create_webpage
cp webpage/fire_graphs.html docs/index.html
echo "Done."
