import os
from unittest import TestCase
from data_store import DataStore
from datetime import datetime

class TestDataStore(TestCase):
    def test_get_data_dir(self):
        source = "/home/me/"
        d = DataStore(source)
        self.assertEqual(source, d.get_data_dir())

    def test_get_filename(self):
        when = datetime(2020, 5, 17)
        d = DataStore("/tmp")
        filename = d.get_filename(when)
        self.assertEqual('/tmp/firedata_2020_05_17.json', filename)

    def test_save_todays_data(self):
        pass # TBD

    def test_save_data(self):
        pass # TBD

    def test_load_all_data(self):
        pass  # TBD

    def test_load_data_day(self):
        pass

    def test_load_data_file(self):
        p = os.getcwd()
        d = DataStore(p)
        f = d.load_data_file("data/data_test/firedata_2020_09_09.json")
        self.assertEqual(4, len(f))