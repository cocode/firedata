"""
Fetch fire info from Federal "InciWeb"
"""
from typing import Optional, Callable, Any

from refresher import Refresh
from data_store import DataStore
import bs4 as bs # type: ignore


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


def get_id(incident):
    """
    Gets a unique id for this incident
    :param incident:
    :return:
    """
    return incident['href']


# Could also use from operator import itemgetter, attrgetter
def summarize(ds, year:int):
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
            id = get_id(fire)
            yesterday_data = yesterday['data']
            yes = [item for item in yesterday_data if get_id(item) == id]
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
        unique_fire_id = get_id(incident)
        if unique_fire_id in check_unique:
            raise Exception(F"Fire ID not unique: {unique_fire_id}")
        check_unique.add(unique_fire_id)


def get_annual_acres_helper(all_data, year):
    """
    This may not work. Not sure if us data has all fires for the year, or only active ones.
    TODO Check the above.
    
    Gets the number of acres burned, for each day of the current (or specified) year.
    Used to generate data for website graphs.

    Unlike cal fire data, where I can just look like a top-level field, I think
    for US I must sum all incidents on each day.

    # TODO Find a better data source.
    # TODO need to parse the year from the filename, and filter to the current year.
    # TODO We should calculate the total acres when we save the data, and add it.

    :param ds:
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
            unique_fire_id = get_id(incident)
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
    data_store = DataStore("data/data_us")
    return data_store


def run():
    fire_url = 'https://inciweb.nwcg.gov/accessible-view/'
    data_store = get_data_store()
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    summarize(data_store)
    annual = get_annual_acres(data_store, 2021)
    print(annual)


if __name__ == "__main__":
    run()
    print("Done.")