# Fetch fire info from cal fire.

# source

import requests
import sys
import json
from datetime import date
import os


# Keys in the json blob returned from cal fire. I only care about "Incidents"
# Incidents
# MatchedIncidentCount
# AllAcres
# AllIncidentCount
# AllFatalities
# AllStructures
# ListIncidents
# AllYearIncidents
from requests import HTTPError
from refresher import Refresh
from data_store import DataStore
import bs4 as bs


def get_size(x:str):
        print("Get size", x)
        if x is None:
            return None

        s = x['Size']
        s = s.strip()
        if not s:
            return 0
        y = s.split()
        z = y[0]
        q = int(z)
        return q


def get_id(fire):
    return fire['href']


# Could also use from operator import itemgetter, attrgetter
def summarize(ds):
    awidth = 14
    dwidth = 10

    jdata = ds.load_all_data()
    jdata_today = jdata[-1]
    if len(jdata) > 1:
        yesterday = jdata[-2]
    else:
        yesterday = None

    if yesterday:
        print(F"{'Acres':>{awidth}} {'Change':>{dwidth}}   {'Incident'}")
    else:
        print(F"{'Acres':>{awidth}}   {'Incident'}")
    incidents = jdata_today
    # already sorted for us by loader
    acres_burned = 0
    acres_added = 0
    growing_fires = 0
    for fire in incidents:
        ab = get_size(fire) # TODO changed from cal_file
        if ab is not None:
            acres_burned += ab # changed

        if yesterday:
            id = get_id(fire)
            yes = [item for item in yesterday if get_id(item) == id]
            assert len(yes) < 2
            f2 = yes[0] if len(yes) else None
            old_size = get_size(f2)
            if ab and f2 and old_size and (old_size != ab):
                delta_a = ab - get_size(f2)
                if delta_a:
                    growing_fires += 1
                acres_added += delta_a
                delta_a = F"{delta_a:>+{dwidth}}"
            else:
                delta_a = F"{' ':{dwidth}}"
            print(F"{get_size(fire):{awidth},} {delta_a}   {fire['Incident']}")
        else:
            print(F"{get_size(fire):{awidth},}   {fire['Incident']}")

    print()
    print(F"Number of incidents.: {len(incidents):20,}")
    print(F"New or growing fires: {growing_fires:20,}")
    print(F"Total acres burned..: {acres_burned:>20,}")
    print(F"New acres burned....: {acres_added:>20,}")

def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    state = "California" # I shoudl start saving for all states, and discarding later.
    # I can't currently change the state, since I don't have historical data for the
    # new state, since I've been throwing it away.
    soup = bs.BeautifulSoup(content, "html5lib")
    table = soup.find("table", {"summary":"This table displays all active incidents."})
    headers = table.find_all("th")
    h2 = []
    for header in headers:
        #print(header.text)
        h2.append(header.text)
    h2.append("href")
    rows = table.find_all("tr")
    incidents = []
    for row in rows[1:]:  # skip header row
        columns = row.find_all("td")
        values = []
        href = None
        for i, col in enumerate(columns):
            if href is None:
                anchor = col.find('a', href=True)
                href = anchor['href']
            values.append(col.text)
        if href:
            values.append(href)
        data = dict(zip(h2, values))

        if not data['State'].startswith(state):
            continue
        incidents.append(data)

    f = sorted(incidents, key=get_size, reverse=True)
    return f


def run():
    fire_url = 'https://inciweb.nwcg.gov/accessible-view/'
    data_store = DataStore("data/data_us")
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    summarize(data_store)


if __name__ == "__main__":
    run()
    print("Done.")