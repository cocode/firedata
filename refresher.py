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
            source_bytes = self.fetch_data(self.url)
            # TODO figure out the encoding (or pass it in, can't always tell)
            if source_bytes:
                source_data = source_bytes.decode("utf-8")
                self.ds.save_source_data(data=source_data, day=today)
            else:
                raise Exception("No source data received in refresh_date")
        else:
            print(F"Using cached data.")

        jdata = self.parse(source_data)
        print(F"JSON data parsed. Len = {len(jdata)}")
        #jdata = json.loads(data) # Convert to json is a quick validation
        self.ds.save_todays_data(jdata)
        print("Data saved.")

    @staticmethod
    def fetch_data(url):
        """
        Fetch the data from the cal fire website.
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

