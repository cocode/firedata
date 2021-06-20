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
        p = os.getcwd()+"/data/data_cal/"
        d = DataStore(p)

        f = d.load_all_data(2019) # Data from previous years should not change.
        count_2019 = len(f)
        self.assertEqual(0, count_2019)

        f = d.load_all_data(2020) # Data from previous years should not change.
        count_2020 = len(f)
        self.assertEqual(42, count_2020)

        f = d.load_all_data(2021)
        count_2021 = len(f)
        self.assertTrue(count_2021 >= 13) # Still changing

        f = d.load_all_data()     # Load all year's data
        count_all = len(f)
        self.assertEqual(count_all, count_2019+count_2020+count_2021)


    def test_load_data_day(self):
        pass

    def test_load_data_file(self):
        p = os.getcwd()+"/data/data_cal/"
        d = DataStore(p)
        f = d.load_data_file("data/data_test/firedata_2020_09_09.json")
        self.assertEqual(4, len(f))

