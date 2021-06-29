from unittest import TestCase

from data_store import DataStore
from get_ca_fire_data import get_delta, summarize, summarize_ytd, filter_by_year
import json


class Test(TestCase):
    def test_get_delta(self):
        with open("data/data_test/firedata_2020_09_09.json") as f:
            older = json.load(f)
        with open("data/data_test/firedata_2020_09_17.json") as f:
            newer = json.load(f)
        a, b = get_delta(newer, older, "not_in_f1_or_f2", 3)
        self.assertEqual("   ", a)
        self.assertEqual(0, b)

        a, b = get_delta(newer, older, "unchanged", 3)
        self.assertEqual("   ", a)
        self.assertEqual(0, b)

        a, b = get_delta(newer, older, "increasing", 4)
        self.assertEqual("  +1", a) # We format with explict leading +/- signs.
        self.assertEqual(1, b)

        a, b = get_delta(newer, older, "decreasing", 3)
        self.assertEqual(" -1",a)
        self.assertEqual(-1, b)

        a, b = get_delta(newer, older, "new", 3)
        self.assertEqual("new", a)
        self.assertEqual(4, b)

        a, b = get_delta(newer, older, "vanished", 3)
        self.assertEqual("   ", a)
        self.assertEqual(0, b)

    def test_summarize(self):
        ds = DataStore("data/data_cal")
        summarize(ds, 2019) # Test for year with no data - just check that it runs.
        summarize(ds, 2020) # Test for year with no data - just check that it runs.
        summarize(ds, 2021) # Test for year with no data - just check that it runs.
        summarize(ds, 2022) # Test for year with no data - just check that it runs.

    def test_summarize_ytd(self):
        ds = DataStore("data/data_cal")
        summarize_ytd(ds, 2019) # Test for year with no data
        summarize_ytd(ds, 2020) # Test for year with no data
        summarize_ytd(ds, 2021) # Test for year with no data
        summarize_ytd(ds, 2022) # Test for year with no data

    def test_filter_by_year(self):
        data = [
            {
                "ArchiveYear": 2001,
            },
            {
                "ArchiveYear": 2002,
            },
            {
                "ArchiveYear": 2003,
            }
        ]
        output = filter_by_year(data, 2002)
        expected = [
            {
                "ArchiveYear": 2002,
            }
        ]
        self.assertEqual(expected, output)

