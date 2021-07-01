import tempfile
from unittest import TestCase
from datetime import date
from data_store import DataStore
from get_ca_fire_data import get_delta, summarize, summarize_ytd, filter_by_year
import get_ca_fire_data
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
        self.assertEqual("  +1", a)  # We format with explict leading +/- signs.
        self.assertEqual(1, b)

        a, b = get_delta(newer, older, "decreasing", 3)
        self.assertEqual(" -1", a)
        self.assertEqual(-1, b)

        a, b = get_delta(newer, older, "new", 3)
        self.assertEqual("new", a)
        self.assertEqual(4, b)

        a, b = get_delta(newer, older, "vanished", 3)
        self.assertEqual("   ", a)
        self.assertEqual(0, b)

    def test_get_annual_acres(self):
        ds = DataStore("data/data_test/data_ca")
        acres_burned, data_count = get_ca_fire_data.get_annual_acres(ds, 2020)
        self.assertEqual(54, acres_burned[-1][3])
        self.assertEqual(2, data_count)

    def test_summarize(self):
        ds = DataStore("data/data_cal")
        summarize(ds, 2019)  # Test for year with no data - just check that it runs.
        summarize(ds, 2020)  # Test for year with no data - just check that it runs.
        summarize(ds, 2021)  # Test for year with no data - just check that it runs.
        summarize(ds, 2022)  # Test for year with no data - just check that it runs.

    def test_summarize2(self):
        ds = DataStore("data/data_test/data_ca2")
        rows, headings, summary, print_headings = summarize(ds, year=None)  # Test for data with no prior day
        self.assertEqual(2,len(rows))
        self.assertEqual(2,summary[0][1])
        self.assertEqual(0,summary[1][1])
        self.assertEqual(50,summary[2][1])
        self.assertEqual(0,summary[3][1])

        print()

    def test_pasre(self):
        parsed = get_ca_fire_data.parse('{"foo":2}')
        self.assertEqual(2, parsed['foo'])

    def test_get_archive_directory(self):
        ad = get_ca_fire_data.get_archive_directory()
        self.assertEqual("data/data_cal/source", ad)

    def test_summarize_ytd(self):
        ds = DataStore("data/data_cal")
        summarize_ytd(ds, 2019)  # Test for year with no data
        summarize_ytd(ds, 2020)  # Test for year with no data
        summarize_ytd(ds, 2021)  # Test for year with no data
        summarize_ytd(ds, 2022)  # Test for year with no data

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

        output = filter_by_year(data, None)
        self.assertEqual(data, output)

    def test_load_most_recent(self):
        with tempfile.TemporaryDirectory() as data_store_dir:
            # Check empty data store
            ds = DataStore(data_store_dir)
            yesterday, today = get_ca_fire_data.load_most_recent(ds)
            self.assertEqual(None, yesterday)
            self.assertEqual([], today)

            # Check data store with one item
            data = {
                "Incidents": [
                    {"AcresBurned":100}
                    ]
            }
            ds.save_todays_data(data)
            yesterday, today = get_ca_fire_data.load_most_recent(ds)
            self.assertEqual(None, yesterday)
            self.assertEqual(data, today)

    def test_get_data(self):
        with tempfile.TemporaryDirectory() as data_store_dir:
            # Check empty data store
            ds = DataStore(data_store_dir)
            one, two, three = get_ca_fire_data.get_data(ds, 2021)
            self.assertIsNone(one)
            self.assertEqual([], two)
            self.assertEqual([], three)

            # Check data store with one item, but filtering by year to zero items.
            year = 2018
            data = {
                "Incidents": [
                    {"AcresBurned": 10037.6, 'ArchiveYear': year}
                ],
            }
            some_date = date(year,1,2)
            ds.save_date_data(some_date, data)

            year = some_date.year
            one, two, three = get_ca_fire_data.get_data(ds, year+1)
            self.assertIsNone(one)
            self.assertEqual(data, two)
            self.assertEqual([], three)
