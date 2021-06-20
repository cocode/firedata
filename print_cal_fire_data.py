"""
This module prints data from Cal Fire Incidents.

It has two main functions.
1. Print daily information, showing how things have changed since the previous day
2. Print annual information, about this whole fire season.

"""

import json
from datetime import date

from refresher import Refresh
from data_store import DataStore
from get_cal_fire_data import summarize, summarize_ytd, get_annual_acres, collect_data


def print_items(stats, format_title='.<', format_value='>20'):
    max_len = len(max(stats, key=lambda x:len(x[0]))[0])
    for item in stats:
        print(F"{item[0]:{format_title}{max_len}}: {item[1]:{format_value}}")
    print()


def sum_and_print(ds, year=None):
    rows, headings, summary, print_headings = summarize(ds, year)
    for heading in print_headings:
        print(heading, end="")
        print(" ", end="")
    print()
    for row in rows:
        for column in row:
            print(column, end="")
            print(" ", end="")
        print()

    print_items(summary, '.<', '>20,')


def run():
    todays_date = date.today()

    data_store = collect_data()
    print(F"Summarizing YTD CAL FIRE data as of..: {todays_date}")

    print("****************************")
    print("        Year To Date        ")
    print("****************************")
    values = summarize_ytd(data_store)
    print_items(values, ".<", ",")

    print("****************************")
    print("        Active Fires        ")
    print("****************************")
    summarize(data_store, year=2021)
    sum_and_print(data_store, year=2021)

    data, days_of_data_found = get_annual_acres(data_store)
    print("Found data for ", days_of_data_found, "days")


if __name__ == "__main__":
    run()
    print("Done.")