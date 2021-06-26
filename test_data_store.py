import os
import tempfile
from unittest import TestCase
from data_store import DataStore
from datetime import date


class TestDataStore(TestCase):
    def test_get_data_dir(self):
        source = "/home/me/"
        d = DataStore(source)
        self.assertEqual(source, d.get_data_dir())

    def test_get_filename(self):
        when = date(2020, 5, 17)
        with tempfile.TemporaryDirectory() as data_store_dir:
            d = DataStore(data_store_dir)
            filename = d.get_filename(when)
            self.assertEqual(F'{data_store_dir}/firedata_2020_05_17.json', filename)

    def test_save_date_data(self):
        with tempfile.TemporaryDirectory() as data_store_dir:
            d = DataStore(data_store_dir)
            today = date.today()
            d.save_date_data(today, {"test_data": "true"})
            data = d.load_data_day(today)
            self.assertTrue(data['test_data'])


    def test_save_data(self):
        pass  # TBD

    def test_load_all_data(self):
        p = os.getcwd() + "/data/data_cal/"
        d = DataStore(p)

        f = d.load_all_data(2017)
        count_2017 = len(f)
        self.assertEqual(0, count_2017)

        # Changing too much, as I load archived of historical data. Comment out for now
        # f = d.load_all_data(2020)
        # count_2020 = len(f)
        # self.assertEqual(79, count_2020)
        #
        # f = d.load_all_data(2021)
        # count_2021 = len(f)
        # self.assertTrue(count_2021 >= 13) # Still changing
        #
        # f = d.load_all_data()     # Load all year's data
        # count_all = len(f)
        # self.assertEqual(count_all, count_2019+count_2020+count_2021)

    def test_load_data_day(self):
        pass

    def test_load_data_file(self):
        p = os.getcwd() + "/data/data_cal/"
        d = DataStore(p)
        f = d.load_data_file("data/data_test/firedata_2020_09_09.json")
        self.assertEqual(4, len(f))

    def test_tempdir(self):
        with tempfile.TemporaryDirectory() as data_store_dir:
            d = DataStore(data_store_dir)
            all = d.load_all_data()
            self.assertEqual(0, len(all))
            dummy = {"firedata": 100}
            d.save_todays_data(dummy)
            all = d.load_all_data()
            self.assertEqual(1, len(all))
            self.assertEqual(dummy, all[0]['data'])

    def test_get_source_filename(self):
        with tempfile.TemporaryDirectory() as data_store_dir:
            d = DataStore(data_store_dir)
            source = "I am source data"
            when = date(2020, 5, 17)
            d.save_source_data(source, when)
            read_data = d.get_source_data(when)
            self.assertEqual(source, read_data)

            # Make sure it doesn't overwrite if not force=true
            s_new = "I am new source data"
            d.save_source_data(s_new, when)
            read_data = d.get_source_data(when)
            self.assertEqual(source, read_data)
            self.assertNotEqual(s_new, read_data)

            # Make sure it does overwrite if force=true
            d.save_source_data(s_new, when, force=True)
            read_data = d.get_source_data(when)
            self.assertNotEqual(source, read_data)
            self.assertEqual(s_new, read_data)



