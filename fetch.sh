PYTHONPATH=$PWD:$PWD/webpage
echo $PYTHONPATH
echo Add other actions to build,
echo test, and deploy your project.
echo $PWD
python3 --version
ls -al
ls -al data
python3 get_cal_fire_data.py
ls -al data
python3 -m webpage.create_webpage
echo "Done."