"""
Fetch, store and filter data fire info from Federal "InciWeb"
"""
import datetime
import json
import os
from typing import Optional, Callable, Any

from refresher import Refresh
from data_store import DataStore
import bs4 as bs # type: ignore

from statistics import Statistics

DATA_STORE_PATH="data/data_us"

stats = Statistics()

def get_size(fire_info:dict):
    """
    Gets the Size field from the dict
    :param fire_info: A dict including the field 'Size' or None.
    :return: Maybe return, None, if fire_info is None, or 0, if 'Size is blank/empty, or the size as an int.
    """
    if fire_info is None:
        # May be None, when checking if a fire existed yesterday.
        return None

    fire_size = fire_info['Size']
    fire_size = fire_size.strip()
    if not fire_size:
        return 0           # Blank value for 'Size'

    y = fire_size.split()  # US data has sizes like "40 Acres"
    assert 2 == len(y)
    numeric_part = y[0]               # Only take the number.
    assert "Acres" == y[1] # Add better handling when we ever see anything other than acres.
    return_value = int(numeric_part)
    return return_value


def get_unique_id(incident):
    """
    Gets a unique id for this incident.
    Originally, we just used href as a unique, but sometimes fires don't get their own URL, and
    get the default "/incident//", or even None.
    :param incident:
    :return:
    """
    has_href = 'href' in incident
    has_name = 'Incident' in incident
    if 'href' in incident:
        href = incident['href']
        if href is not None and href != "/incident//":
            return href

    if 'Incident' in incident:
        name = incident['Incident']
        if name:
            return name

    raise Exception(F"No unique id for incident {incident}")

# Old name. Makes it unclear what the results are.
def summarize(ds, year: int):
    return get_daily_delta(ds, year)


def get_daily_delta(ds, year: int):
    """
    This function gives information about the change in fires from one day to the next,
    it does NOT have overall information about the fires for the year.
    :param ds:
    :param year:
    :return: Number of acres consumed by fires that are currently burning
    """
    print("Summary for ", year if year else "all years.")
    awidth = 14
    dwidth = 10

    jdata = ds.load_all_data(filter_to_year=year)
    if len(jdata) == 0:
        return 0
    jdata_today = jdata[-1]
    if len(jdata) > 1:
        yesterday = jdata[-2]
    else:
        yesterday = None

    if yesterday:
        print(F"{'Acres':>{awidth}} {'Change':>{dwidth}}   {'Incident'}")
    else:
        print(F"{'Acres':>{awidth}}   {'Incident'}")
    incidents = jdata_today['data']
    # already sorted for us by loader
    acres_burned = 0
    acres_added = 0
    growing_fires = 0
    for fire in incidents:
        ab = get_size(fire)  # TODO changed from cal_file
        if ab is not None:
            acres_burned += ab # changed

        if yesterday:
            id = get_unique_id(fire)
            yesterday_data = yesterday['data']
            yes = [item for item in yesterday_data if get_unique_id(item) == id]
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
    return acres_burned


def get_annual_acres_helper(all_data, year, previous_data=None, cummulative=False):
    return stats.get_annual_acres_helper(all_data, year=year, previous_data=previous_data,
                                         get_unique_id=get_unique_id, get_size=get_size, cummulative=cummulative)


def get_annual_acres(ds:DataStore, year, state=None):
    def filter_by_state(x):
        return x['State'].startswith(state)

    include_function: Optional[Callable[[Any], Any]]
    if state:
        include_function = filter_by_state
    else:
        include_function = None
    all_data = ds.load_all_data(year, include=include_function)
    if year is None:
        previous_data = None
    else:
        # TODO This doesn't work, if we use the create_webpage option to start the graph at other than the first day.
        previous_data = ds.load_all_data(year - 1, include=include_function)
    return get_annual_acres_helper(all_data, year=year, previous_data=previous_data)


def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    soup = bs.BeautifulSoup(content)
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

        incidents.append(data)

    f = sorted(incidents, key=get_size, reverse=True)
    return f


def get_data_store():
    data_store = DataStore(DATA_STORE_PATH)
    return data_store


def run():
    fire_url = 'https://inciweb.nwcg.gov/accessible-view/'
    data_store = get_data_store()
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    summarize(data_store, year=None)
    annual = get_annual_acres(data_store, 2021)
    print(annual)


def get_archive_directory():
    archive_directory = DATA_STORE_PATH+"/source"
    return archive_directory


if __name__ == "__main__":
    run()
    print("Done.")