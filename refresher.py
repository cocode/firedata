"""
Fetches today's data from CalFire, but only if we don't already have it.
"""
import requests
from datetime import date
import os
import json
from requests import HTTPError
from data_store import DataStore


class Refresh:
    def __init__(self, url, ds: DataStore, parse):
        self.url = url
        self.ds: DataStore = ds
        self.parse = parse

    def pt(self, a):
        return F"Refresher Patch_{a}_test"

    def refresh(self):
        """
        Fetch today's fire data, if we don't already have a file for today. This allows us
        to not hit their server every time I want to make a change.
        :return: None - Data is written to the data store.
        """

        today: date = date.today()
        self.refresh_date(today)

    def refresh_date(self, today):
        """
        Fetch fire data for "today".
        For testing, today can be any date, but in production, it's going to fetch
        the data from the remote site right now, so today's data is all you can get.
        :param today: The date to use when saving to the data store.

        :return: None - the data is written to the data store.
        """
        filename_today = self.ds.get_filename(today)
        if os.path.exists(filename_today):
            return # TODO check for source more recent than data?
        # Check for cached data.
        source_data: str = self.ds.get_source_data(today)
        if source_data is None:
            print(F"Fetching data from {self.url}")
            response = requests.get(self.url)
            if response.status_code != 200:
                print("Request failed: ", response.status_code)
                raise HTTPError  # Not quite right, as request.get can also throw HTTPError
            source_bytes = response.content
            # TODO figure out the encoding (or pass it in, can't always tell)
            if source_bytes:
                source_data = source_bytes.decode("utf-8")
                self.ds.save_source_data(data=source_data, day=today)
            else:
                raise EOFError("No source data received in refresh_date")

        jdata = self.parse(source_data)
        print(F"JSON data parsed. Len = {len(jdata)}")
        #jdata = json.loads(data) # Convert to json is a quick validation
        self.ds.save_todays_data(jdata)
        print("Data saved.")

