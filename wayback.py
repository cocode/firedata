"""
Fetch archival copies of a webpage from the internet archive.

First, fetch them with this file, then run "run_wayback" in get_us_fire_data to parse these files,
and put them into the datastore in json.

Note: I'm currently only downloading ones I don't have, but some of the ones I already have are california
only. I should delete those, and redownload. They can be spotted by being much smaller than the other files.
"""
import datetime
import json
import os

import get_cal_fire_data
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


def is_available(url):
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


def fetch_all_snapshots(archive_dir, wayback_filename, target_url):
    """
    Fetch all the snapshots for the website.
    :return:
    """
    # Read the list of snapshots.
    with open(wayback_filename) as f:
        data = f.read()

    url_template = "http://web.archive.org/web/{timestamp}/{target_url}"
    snapshots = data.split("\n")
    data_store = DataStore(archive_dir)
    pages_downloaded = 0
    pages_failed = 0
    for snapshot in snapshots:
        fields = snapshot.split()
        if len(fields) < 1:
            print("Bad fields. End of data?")
            break
        date_string = fields[1]
        assert 14 == len(date_string)
        ymd = date_string[:8]
        year = int(date_string[:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        assert 1900 < year < 2100 and 1 <= month <= 12 and 1 <= day <=31
        date_of_fire = datetime.date(year,month, day)
        filename = F"firedata_{year}_{month:02}_{day:02}.html"
        path = os.path.join(archive_dir, filename)
        if os.path.exists(path):
            print("Not replacing ", path)
            continue
        else:
            print("Downloading for ", path)
        url = url_template.format(timestamp=date_string, target_url=target_url)
        print(url)

        page = fetch(url)
        if page is None:
            print("Fetching above url failed.")
            pages_failed +=1
            continue

        pages_downloaded += 1
        with open(path, "wb") as f:
            f.write(page)
        print("Page saved")
        sleep(2)
    return pages_downloaded, pages_failed

def fetch_us():
    # I fetched the snapshot data manually, and saved it:
    # curl http://web.archive.org/cdx/search/cdx?url=inciweb.nwcg.gov/accessible-view/
    archive_dir = get_us_fire_data.get_archive_directory()
    pages, pages_failed = fetch_all_snapshots(archive_dir, "wayback_us_snapshots.txt", target_url='https://inciweb.nwcg.gov/accessible-view/')
    return pages, pages_failed

def fetch_ca():
    archive_dir = get_cal_fire_data.get_archive_directory()
    pages, pages_failed = fetch_all_snapshots(archive_dir, "wayback_ca_snapshots.txt", target_url='https://www.fire.ca.gov/umbraco/Api/IncidentApi/GetIncidents')
    return pages, pages_failed

pages, pages_failed = fetch_us()
print(F"{pages} pages downloaded, {pages_failed} pages failed to download.")
#one_snapshot_url = "http://web.archive.org/web/20210603183442/https://inciweb.nwcg.gov/accessible-view/"
#page = fetch(one_snapshot_url)
#print(page)
# is_avaliable("https://inciweb.nwcg.gov/accessible-view/")