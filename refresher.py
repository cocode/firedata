"""
Fetches today's data from CalFire, but only if we don't already have it.
"""
import requests
from datetime import date
import os
import json
from requests import HTTPError


class Refresh:
    def __init__(self, url, ds, parse):
        self.url = url
        self.ds = ds
        self.parse = parse

    def refresh(self):
        """
        Fetch today's fire data, if we don't already have a file for today. This allows us
        to not hit their server every time I want to make a change.
        :return: Fire data as json
        """
        today = date.today()
        filename_today = self.ds.get_filename(today)
        if os.path.exists(filename_today):
            return
        print(F"Fetching data from {self.url}")
        data = self.fetch_data(self.url)
        jdata = self.parse(data)
        #jdata = json.loads(data) # Convert to json is a quick validation
        self.ds.save_todays_data(jdata)

    @staticmethod
    def fetch_data(url):
        '''
        Fetch the data from the cal fire website.
        :return:
        '''
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

        return response.content

