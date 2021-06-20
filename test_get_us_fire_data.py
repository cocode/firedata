from unittest import TestCase
from get_us_fire_data import get_size, get_annual_acres_helper
from data_store import DataStore


class Test(TestCase):
    def test_get_size(self):
        f = None
        self.assertIsNone(get_size(f))
        f = {}
        with self.assertRaises(KeyError):
            self.assertIsNone(get_size(f))
        f = {"Size":"40 Acres"}
        self.assertEqual(40, get_size(f))

    def test_get_annual_acres(self):
        ds = DataStore("data/data_test/us")
        all_data = ds.load_all_data()
        one_day = all_data[0:1]

        total_by_days, overall_total = get_annual_acres_helper(one_day, None)
        self.assertEqual(1, len(total_by_days))
        first_day = total_by_days[0]
        self.assertEqual(None, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(10, first_day[2])
        self.assertEqual(234, first_day[3])

        total_by_days, overall_total = get_annual_acres_helper(all_data, None)
        first_day = total_by_days[0]
        self.assertEqual(None, first_day[0])
        self.assertEqual(8, first_day[1])
        self.assertEqual(10, first_day[2])
        self.assertEqual(234, first_day[3])

        v = total_by_days[1]
        self.assertEqual(None, v[0])
        self.assertEqual(8, v[1])
        self.assertEqual(11, v[2])
        self.assertEqual(100, v[3])
        print(total_by_days)