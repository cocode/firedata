"""
Fetch archival copies of a webpage from the internet archive.

First, fetch them with this file, then run "run_wayback" in get_us_fire_data to parse these files,
and put them into the datastore in json.
"""
import datetime
import json
import os

from data_store import DataStore
import get_us_fire_data
from time import sleep
from urllib.error import HTTPError

import requests
import urllib


def fetch(url):
    """
    :param url: The url to fetch data from.
    :return: The contents of the webpage, or None
    """

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Request failed: ", response.status_code)
            return None

    except HTTPError as e:
        print(F'Got an error: {e}')
        return None
    except Exception as e:
        print(F'Other exception: {e}')
        return None
    print(F"HTTP request succeed. Response size={len(response.content)}")
    return response.content


def is_avaliable(url):
    wayback_url = "http://archive.org/wayback/available?url="
    encoded = urllib.parse.quote_plus(url)
    full_url = wayback_url + encoded
    print(full_url)
    data = fetch(full_url)
    if data is not None:
        print(data)
    values = json.loads(data)
    print(json.dumps(values, indent=4))
    return data


def fetch_all_snapshots():
    """
    Fetch all the snapshots for the us fire website. (can generalize later)
    :return:
    """
    # I fetched the data once, and saved it:
    # curl http://web.archive.org/cdx/search/cdx?url=inciweb.nwcg.gov/accessible-view/
    with open("wayback_us_snapshots.txt") as f:
        data = f.read()

    archive_dir = get_us_fire_data.get_archive_directory()

    url_template = "http://web.archive.org/web/{timestamp}/https://inciweb.nwcg.gov/accessible-view/"

    snapshots = data.split("\n")
    data_store = DataStore(archive_dir)
    for snapshot in snapshots:
        fields = snapshot.split()
        date_string = fields[1]
        assert 14 == len(date_string)
        ymd = date_string[:8]
        year = int(date_string[:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        if year < 2021:
            print("Skipping ", year)
            continue
        assert 1900 < year < 2100 and 1 <= month <= 12 and 1 <= day <=31
        date_of_fire = datetime.date(year,month, day)
        filename = F"firedata_{year}_{month:02}_{day:02}.html"
        path = os.path.join(archive_dir, filename)
        if os.path.exists(path):
            print("Not replacing ", path)
            continue
        else:
            print("Downloading for ", path)
        url = url_template.format(timestamp=date_string)
        print(url)

        page = fetch(url)
        if page is None:
            print("Fetching above url failed.")

        with open(path, "wb") as f:
            f.write(page)
        print("Page saved")
        #print(date_string)
        break # for now, only do one. Maybe skip ones that are already downloaded.

fetch_all_snapshots()
#one_snapshot_url = "http://web.archive.org/web/20210603183442/https://inciweb.nwcg.gov/accessible-view/"
#page = fetch(one_snapshot_url)
#print(page)
# is_avaliable("https://inciweb.nwcg.gov/accessible-view/")