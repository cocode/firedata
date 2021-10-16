"""
This module fetches and prints data from Cal Fire Incidents. this is version 2, which doesn't pull the json,
it just gets the acres burner from the HTML


"""

import json
import re
from datetime import date

from refresher import Refresh
from data_store import DataStore
import bs4 as bs  # type: ignore




def filter_by_year(sorted_fires, year: int):
    """
    Limit data to the specified year. If year is None, then return without filtering.
    TODO is this redundant, now that the DataStore can filter by year?
    :param sorted_fires:
    :param year: Int year, or None
    :return:
    """
    if year:
        filtered_fires = []
        for ii in sorted_fires:
            archive_year = ii['ArchiveYear']
            if archive_year == year:
                filtered_fires.append(ii)
    else:
        filtered_fires = sorted_fires
    return filtered_fires


def get_incidents(todays_data):
    """
    Get data from the "Incidents" field of the downloaded data, which is currently or recently
    burning fires.

    :param todays_data:
    :return: a sorted list of incidents.
    """
    incidents = todays_data["Incidents"]
    sorted_fires = sorted(incidents, reverse=True,
                     key=lambda x: x["AcresBurned"] if x["AcresBurned"] is not None else 0)
    return sorted_fires


def load_most_recent(ds: DataStore):
    """
    Loads the most recent two data points from the data store.

    :param ds:
    :return: tuple (yesterday's data, today's data)
    """
    jdata = ds.load_all_data()
    if len(jdata) < 1:
        return None, []
    jdata_today = jdata[-1]['data']
    if len(jdata) > 1:
        yesterday = jdata[-2]['data']["Incidents"]
    else:
        yesterday = None
    return yesterday, jdata_today


def get_data(ds:DataStore, year: int):
    """
    Loads the most recent two data points, which should be today and yesterday (or yesterday and the
    day before, depending on the time of day.
    :param ds:
    :param year:
    :return:
    """
    yesterday, jdata_today = load_most_recent(ds)
    if len(jdata_today) == 0:
        return None, [], []
    sorted_fires = get_incidents(jdata_today)
    filtered_fires = filter_by_year(sorted_fires, year)
    return yesterday, jdata_today, filtered_fires


def get_annual_acres(ds:DataStore, year:int):
    """
    Gets the number of acres burned, for each day of the current (or specified) year.
    Used to generate data for website graphs.
    Note: CA data is already cumulative, so we don't need a cumulative option. We could add a NON-cummulative option.

    :param ds:
    :param year:
    :return: list of tuples (year, month, day, acres burned that day).
    """
    all_data = ds.load_all_data(year)
    acres_burned = []
    for meta_data in all_data:
        day_data = meta_data['data']
        days_year = meta_data["_year"]
        if year is not None:
            assert(days_year == year)
        for item in day_data:
            if day_data[0][1] != 'Acres':
                continue
            ab = day_data[0][0]
            ab = int(ab)
            acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], ab))
    return acres_burned, len(all_data)


def summarize_ytd(ds: DataStore, year: int):
    """
    Summarize the year-to-date data in the most recent day's data from calfire.
    :param ds: the data store
    :param year: the year to summarize
    :return: list of [title, value]
    """
    return_value = []
    all_data = ds.load_all_data(year)
    if len(all_data) == 0:
        return [[F"No data found for year", year]]
    most_recent_day = all_data[-1]['data']
    if 'AllAcres' in most_recent_day:
        all_acres = most_recent_day['AllAcres']
        return_value.append(["Total acres burned this year to date", all_acres])

    else:
        all_acres = None
    key = "AllYearIncidents"
    if not key in most_recent_day:
        return_value.append(["No annual incident data found", 0])
        return

    all_year_incidents = most_recent_day[key]
    computed_acres = 0 # Should be the same as the top level value we get, but check.
    # incident_count = len(incidents)
    for incident in all_year_incidents:
        acres_burned = incident.get('AcresBurnedDisplay', "0")
        acres_burned = acres_burned.strip()
        acres_burned = acres_burned.replace(",", "")
        if not acres_burned:
            continue
        acres_burned = int(acres_burned)
        computed_acres += acres_burned

    if all_acres != computed_acres:
        return_value.append(["Total acres burned computed", computed_acres])

    return_value.append(["Total incidents reported year to date", len(all_year_incidents)])
    return return_value

def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    soup = bs.BeautifulSoup(content)
    section = soup.find("div",  {"class": "incidents-overview"})
    h4 = section.find_all("h4")
    info = []
    for item in h4:
        t = item.text
        number, units = t.split()
        number = number.replace(",","")
        info.append((number, units))
    return info


DATA_STORE_PATH="data/data_ca"  # new repository


def get_data_store():
    data_store = DataStore(DATA_STORE_PATH)
    return data_store

# Only used by wayback. Going forward, use new get/save source data methods in data_store.
def get_archive_directory():
    archive_directory = DATA_STORE_PATH+"/source"
    return archive_directory


def fetch():
    cal_fire_url = 'https://www.fire.ca.gov/incidents/'
    data_store = get_data_store()
    refresher = Refresh(cal_fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    return data_store


def run():
    todays_date = date.today()
    print(F"Collecting CAL FIRE data on: {todays_date}")
    data_store = fetch()
    data, days_of_data_found = get_annual_acres(data_store, year=None) # Get data for all years.
    print("Now have data for ", days_of_data_found, "days, total.")
    # TODO print starting and ending dates.


if __name__ == "__main__":
    run()       # pragma: no cover
    foo = get_annual_acres(get_data_store(), 2021)
    print(foo)
    print("Done.") # pragma: no cover