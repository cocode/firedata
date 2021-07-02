from unittest import TestCase

import get_us_fire_data
from get_us_fire_data import get_size, get_annual_acres_helper
from data_store import DataStore


class Test(TestCase):
    def test_get_size(self):
        f = None
        self.assertEqual(0, get_size(f))
        f = {}
        self.assertEqual(0, get_size(f))
        f = {"Size":"40 Acres"}
        self.assertEqual(40, get_size(f))
        f = {"Size":"   "}
        self.assertEqual(0, get_size(f))


    def test_get_annual_acres2(self):
        ds = DataStore("data/data_test/us2")
        all_data = ds.load_all_data()
        one_day = all_data[0:1]

        total_by_days, overall_total = get_annual_acres_helper(one_day, year=None)
        self.assertEqual(1, len(total_by_days))
        first_day = total_by_days[0]
        self.assertEqual(2020, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(10, first_day[2])
        self.assertEqual(234, first_day[3])

        total_by_days, overall_total = get_annual_acres_helper(all_data, None)
        first_day = total_by_days[0]
        self.assertEqual(2020, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(10, first_day[2])
        self.assertEqual(234, first_day[3])

        v = total_by_days[1]
        self.assertEqual(2020, v[0])
        self.assertEqual(8, v[1])
        self.assertEqual(11, v[2])
        self.assertEqual(100, v[3])
        print(total_by_days)

    def test_get_annual_acres(self):
        ds = DataStore("data/data_test/us")

        year = 2019
        all_data_2019 = ds.load_all_data(year)
        total_by_days, overall_total = get_annual_acres_helper(all_data_2019, year=year)
        self.assertEqual(1, len(total_by_days))
        first_day = total_by_days[0]
        self.assertEqual(year, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(10, first_day[2])
        self.assertEqual(197, first_day[3])

        year = 2020
        all_data_2020 = ds.load_all_data(year)
        total_by_days, overall_total = get_annual_acres_helper(all_data_2020, year=year, previous_data=all_data_2019)
        first_day = total_by_days[0]
        self.assertEqual(year, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(11, first_day[2])
        self.assertEqual(9, first_day[3])




    def test_summarize(self):
        ds = DataStore("data/data_us")
        acres_burned = get_us_fire_data.summarize(ds, 2017)
        self.assertEqual(0, acres_burned)

        acres_burned = get_us_fire_data.summarize(ds, 2020)
        self.assertEqual(4250771, acres_burned)
        acres_burned = get_us_fire_data.summarize(ds, year=None)

        ds = DataStore("data/data_test/us_no_yesterday")
        acres_burned = get_us_fire_data.summarize(ds, 2019)
        self.assertEqual(197, acres_burned)




