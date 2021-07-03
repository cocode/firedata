from datetime import date
from unittest import TestCase

import get_az_fire_data
from data_store import DataStore


class Test(TestCase):
    def test_parse(self):
        data_store = get_az_fire_data.get_data_store()
        data = data_store.get_source_data(date(2021, 6, 25))
        results = get_az_fire_data.parse(data)
        self.assertEqual(921, results["number_of_fires"])
        self.assertEqual(468289, results["acres_burned"])


    def test_get_annual_acres(self):
        data_store = DataStore("data/data_test/data_az")
        # Should be no data in 2019, test for that.
        days, totals = get_az_fire_data.get_annual_acres(data_store, 2019)
        self.assertEqual(0, len(days))

        days, total = get_az_fire_data.get_annual_acres(data_store, 2021)
        self.assertEqual(1, len(days))
        self.assertEqual(1, total)
        self.assertEqual(2021, days[0][0])
        self.assertEqual(6, days[0][1])
        self.assertEqual(26, days[0][2])
        self.assertEqual(468290, days[0][3])
