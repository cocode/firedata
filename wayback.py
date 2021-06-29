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

import get_ca_fire_data
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


def run_parsing(archive_directory, data_store, parse):
    """
    This method takes already downloaded snapshots of a webpage, and extracts the fire data
    using parse(), and saves it to the datastore, but only if it's not already present.
    :return:
    """
    files = os.listdir(archive_directory)
    counter = 0
    count_nr = 0
    for filename in files:
        if not filename.endswith(".html"):
            continue
        parts = filename[:-len(".html")].split('_')
        assert len(parts) == 4
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        assert 1900 < year < 2100 and 1 <= month <= 12 and 1 <= day <=31
        path = archive_directory + "/" + filename
        with open(path) as f:
            archive = f.read()
        fire_data = parse(archive)
        # Tag the entry with some meta data, so we can find them again, if we need to redo things.
        if type(fire_data) == dict:
            fire_data['_source'] = path
        elif type(fire_data) == list:
            # Problem: We use href as a unique ID a fire. It turns out not all fires have a unique href ("/incident//)
            # instead of the usual "/incident/1234".
            for incident in fire_data:
                incident['_source'] = path
                # We use the href as a unique identifier. We want the original href, not the internet archive version.
                href:str = incident['href']
                assert href.startswith("/web/")
                index = href.find("/incident/")
                assert index != -1
                href = href[index:]
                incident['href'] = href
        #print(json.dumps(fire_data, indent=4))
        data_date = datetime.date(year,month, day)
        already_exists = data_store.does_data_exist(data_date) # TODO Move up.
        if already_exists:
            print(F"Skipping {os.path.join(path, filename)}")
        else:
            print(F"Writing from {filename}")
            data_store.save_date_data(data_date, fire_data)
            counter += 1
        print
    return counter


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
    pages_downloaded = 0
    pages_failed = 0
    pages_skipped = 0
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
            pages_skipped += 1
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
    return pages_downloaded, pages_failed, pages_skipped


def fetch_us():
    # I fetched the snapshot data manually, and saved it:
    # curl http://web.archive.org/cdx/search/cdx?url=inciweb.nwcg.gov/accessible-view/
    archive_dir = get_us_fire_data.get_archive_directory()
    pages, pages_failed, pages_skipped = fetch_all_snapshots(archive_dir, "wayback_us_snapshots.txt", target_url='https://inciweb.nwcg.gov/accessible-view/')
    print(F"{pages} pages downloaded, {pages_failed} pages failed to download.  {pages_skipped} pages skipped. Total: {pages+pages_failed+pages_skipped}.")
    return pages, pages_failed, pages_skipped


def fetch_ca():
    archive_dir = get_ca_fire_data.get_archive_directory()
    pages, pages_failed, pages_skipped = fetch_all_snapshots(archive_dir, "wayback_ca_snapshots.txt", target_url='https://www.fire.ca.gov/umbraco/Api/IncidentApi/GetIncidents')
    print(F"{pages} pages downloaded, {pages_failed} pages failed to download.  {pages_skipped} pages skipped. Total: {pages+pages_failed+pages_skipped}.")
    return pages, pages_failed, pages_skipped


def update_from_archive_us():
    archive_dir = get_us_fire_data.get_archive_directory()
    data_store = get_us_fire_data.get_data_store()
    counter = run_parsing(archive_dir, data_store, get_us_fire_data.parse)
    print(F"Update {counter} records.")


def update_from_archive_ca():
    archive_dir = get_ca_fire_data.get_archive_directory()
    data_store = get_ca_fire_data.get_data_store()
    counter = run_parsing(archive_dir, data_store, get_ca_fire_data.parse)
    print(F"Update {counter} records.")


if __name__ == "__main__":
    fetch_us()
    update_from_archive_us()

    fetch_ca()
    # The file data/data_cal/source/firedata_2021_04_03.html is in XML format. Don't download it. I made a zero length version.
    update_from_archive_ca()

    # one_snapshot_url = "http://web.archive.org/web/20210603183442/https://inciweb.nwcg.gov/accessible-view/"
    # page = fetch(one_snapshot_url)
    # print(page)
