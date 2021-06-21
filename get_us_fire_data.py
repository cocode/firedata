"""
Fetch fire info from Federal "InciWeb"
"""
import datetime
import json
import os
from typing import Optional, Callable, Any

from refresher import Refresh
from data_store import DataStore
import bs4 as bs # type: ignore

DATA_STORE_PATH="data/data_us"


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


def verify_ids_unique(incidents):
    """
    Make sure fire ids are unique. Don't trust your data sources!
    Raises an Exception on duplicate
    :param incidents:
    :return: None
    """
    check_unique = set()
    for incident in incidents:
        unique_fire_id = get_unique_id(incident)
        if unique_fire_id in check_unique:
            raise Exception(F"Fire ID not unique: {unique_fire_id}")
        check_unique.add(unique_fire_id)


def get_annual_acres_helper(all_data, year):
    """
    Gets the number of acres burned, for each day of the current (or specified) year.
    Used to generate data for website graphs.

    Unlike cal fire data, where I can just look like a top-level field, I think
    for US I must sum all incidents on each day.

    # TODO Find a better data source.
    # TODO need to parse the year from the filename, and filter to the current year.
    # TODO We should calculate the total acres when we save the data, and add it.

    :param year:
    :return: list of tuples of (year, month, day, acres_burned)
    """
    acres_burned = []
    last_burned = {}
    overall_total_acres_burned = 0
    for meta_data in all_data:
        day_data = meta_data['data']
        days_year = meta_data["_year"]
        if year is not None and days_year != year:
            continue
        days_total = 0

        # Make sure fire ids are unique.
        verify_ids_unique(day_data)

        for incident in day_data:
            unique_fire_id = get_unique_id(incident)
            ab = incident['Size']
            ab = ab.strip()
            if ab:
                if " " in ab:
                    ab = ab.split()
                    assert ab[1]=='Acres'
                    ab = ab[0]  # Take off the word "acres"
                burned_as_of_today = int(ab)  # What is this file's total burned acres, as of today.
                # Compute delta between current total for this fire, and yesterdays, so we get
                # acres burned today.
                if unique_fire_id in last_burned:
                    previous_total = last_burned[unique_fire_id]
                    last_burned[unique_fire_id] = burned_as_of_today
                    change_in_acres_burned = burned_as_of_today - previous_total  # Get change since last data point.
                else:
                    # New fire. Change is total acres burned today.
                    change_in_acres_burned = burned_as_of_today
                    last_burned[unique_fire_id] = burned_as_of_today

                days_total += change_in_acres_burned
        acres_burned.append((year, meta_data["_month"], meta_data["_day"], days_total))
        overall_total_acres_burned += days_total
    return acres_burned, overall_total_acres_burned


def get_annual_acres(ds:DataStore, year, state=None):
    def filter_by_state(x):
        return x['State'].startswith(state)

    include_function: Optional[Callable[[Any], Any]]
    if state:
        include_function = filter_by_state
    else:
        include_function = None
    all_data = ds.load_all_data(year, include=include_function)
    return get_annual_acres_helper(all_data, year)


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


def run_wayback():
    """
    This method takes already downloaded snapshots of a webpage, and extracts the fire data
    using parse(), and saves it to the datastore, but only if it's not already present.
    :return:
    """
    archive_directory = get_archive_directory()
    files = os.listdir(archive_directory)
    for filename in files:
        if not filename.endswith(".html"):
            continue
        parts = filename[:-len(".html")].split('_')
        assert len(parts) == 4
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        assert 1900 < year < 2100 and 1 <= month <= 12 and 1 <= day <=31
        print(filename)
        path = archive_directory + "/" + filename
        with open(path) as f:
            archive = f.read()
        fire_data = parse(archive)
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
        data_store = get_data_store()
        data_date = datetime.date(year,month, day)
        already_exists = data_store.does_data_exist(data_date)
        if already_exists:
            print(F"Skipping {filename}")
        else:
            print(F"Writing from {filename}")
            data_store.save_date_data(data_date, fire_data)
        print


if __name__ == "__main__":
    #run()
    run_wayback()
    print("Done.")