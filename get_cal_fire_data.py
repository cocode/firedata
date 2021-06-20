"""
This module fetches and prints data from Cal Fire Incidents.

It has two main functions.
1. Print daily information, showing how things have changed since the previous day
2. Print annual information, about this whole fire season.

"""

import requests
import sys
import json
from datetime import date
import os
import io

from requests import HTTPError
from refresher import Refresh
from data_store import DataStore


# Keys in the json blob returned from cal fire. Comments are my current understanding
# Incidents - Actively burning and very recent events.
# MatchedIncidentCount
# AllAcres - The total number of acres burned this year.
# AllIncidentCount
# AllFatalities - The total number of fatalities this year.
# AllStructures - The total number of structures burned this year.
# ListIncidents
# AllYearIncidents - All the incidents that have occurred this year.


# f-strings in python suck at handling None, so this class helps
def sub(fire, key, width: int, f=None):
    if key in fire and fire[key] is not None:
        value = F"{fire[key]:{width},}"
    else:
        value = F"{'~':>{width}}"
    return value


def get_delta(f1, f2, key, width: int=10):
    """
    finds and formats the difference between the one key value in two dicts.
    :param f1: Today's dict
    :param f2: Yesterday's dict
    :param key: The key to check in the dicts.
    :param width: The desired width of the field
    :return: A tuple of formatted string of the delta, and the delta as a number
    """
    def blank(fill = ' '):
        return F"{fill:{width}}"

    if key not in f1 or f1[key] is None:
        return blank(), 0  #todo Should this print an error message?
    elif f2 is None or key not in f2 or f2[key] is None:
        return blank(F'{"new":>{width}}'), float(f1[key])

    delta = f1[key] - f2[key]
    if delta == 0:
        return blank(), 0

    return F"{delta:>+{width},}", delta


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
    # I believe "Incidents" contains only active fires.
    incidents = todays_data["Incidents"]
    sorted_fires = sorted(incidents, reverse=True,
                     key=lambda x: x["AcresBurned"] if x["AcresBurned"] is not None else 0)
    return sorted_fires


def load_most_recent(ds: DataStore):
    """
    Loads the most recent two data points from the data store.
    :param ds:
    :return:
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

    :param ds:
    :param year:
    :return: tuple of number of acres burned in the given year, and length of all_data.
    """
    all_data = ds.load_all_data(year)
    acres_burned = []
    for meta_data in all_data:
        day_data = meta_data['data']
        days_year = meta_data["_year"]
        if days_year != year:
            continue
        ab = day_data['AllAcres']
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


def summarize(ds, year:int):
    """
    Print a summary of information about fires in the database. This is a summary that compares to the
    previous day's data. This may be wrong if we skipped collecting for a day.
    :param ds: The data store to load data from.
    :param year: If not None, the default, then only print data for the given year.
    :return:
    """
    dwidth = 11
    awidth = 14
    pwidth = 5

    yesterday, jdata_today, filtered_fires = get_data(ds, year)
    if yesterday:
        print_headings = [F"{'Acres Burned':>{awidth}}",  F"{'Change':>{dwidth}}", F"{'%Cont':{pwidth}}",  F"{'Change':>{dwidth}}", F"{'Incident Name'}"]
    else:
        # TODO print both cases the same. And shouldn't the second column be "%Cont", not "Change", if no prior day's data?
        print_headings = [F"{'Acres Burned':>{awidth}}",  F"{'Change':>{dwidth}}", F"{'Incident Name'}"]

    acres_burned = 0
    acres_added = 0 # Number of new acres burned since yesterday
    growing_fires = 0 # Includes new fires.
    rows = []
    for fire in filtered_fires:
        row = []
        ab = fire.get('AcresBurned', 0)
        if ab is not None:
            acres_burned += fire.get('AcresBurned', 0)

        if yesterday:
            id = fire['UniqueId']
            yes = [item for item in yesterday if item["UniqueId"] == id]
            assert len(yes) < 2
            f2 = yes[0] if len(yes) else None
            delta_a, da = get_delta(fire, f2, 'AcresBurned', width=dwidth)
            acres_added += da
            if da:
                growing_fires += 1
            delta_c,dc = get_delta(fire, f2, 'PercentContained', width=dwidth)
            # if 'AcresBurned' in f2 and f2['AcresBurned'] is not None:
            #     delta_a = fire['AcresBurned'] - f2['AcresBurned']
            # else:
            #     delta_a = "~"
            row = [sub(fire,'AcresBurned',awidth), delta_a, sub(fire,'PercentContained',5), delta_c, fire['Name']]
        else:
            row = [sub(fire,'AcresBurned',awidth), "N/A", sub(fire,'PercentContained',5), "N/A", fire['Name']]
        rows.append(row)

    summary = [
        [F"Number of active incidents", len(filtered_fires)],
        [F"New or growing fires", growing_fires],
        [F"Total acres burned, active fires", acres_burned],
        [F"New acres burned", acres_added]
    ]

    headings = ['Acres Burned', 'Change', '% Contained', 'Change', 'Incident Name']

    return rows, headings, summary, print_headings



def parse(data):
    """
    Loads the data from the cal file website. It comes down in json string format.
    :param data:
    :return:
    """
    return json.loads(data)


def collect_data():
    cal_fire_url = 'https://www.fire.ca.gov/umbraco/Api/IncidentApi/GetIncidents'
    cal_fire_dir = "data/data_cal"
    data_store = DataStore(cal_fire_dir)
    refresher = Refresh(cal_fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    return data_store


def run():
    todays_date = date.today()
    print(F"Collecting CAL FIRE data on: {todays_date}")
    data_store = collect_data()
    data, days_of_data_found = get_annual_acres(data_store, year=None) # Get data for all years.
    print("Nnow have data for ", days_of_data_found, "days, total.")
    # TODO print starting and ending dates.


if __name__ == "__main__":
    run()
    print("Done.")