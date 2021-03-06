from datetime import date
from unittest import TestCase

import get_wa_fire_data
import utilities
from data_store import DataStore


class Test(TestCase):
    def test_get_size(self):
        f = None
        self.assertEqual(0, get_wa_fire_data.get_size(f))
        f = {}
        self.assertEqual(0, get_wa_fire_data.get_size(f))
        f = {"Acres":"40 Acres"}
        self.assertEqual(40, get_wa_fire_data.get_size(f))
        f = {"Acres":" ,"}
        self.assertEqual(0, get_wa_fire_data.get_size(f))
        f = {"Acres":"     "}
        self.assertEqual(0, get_wa_fire_data.get_size(f))

    def test_get_containment(self):
        f = None
        self.assertEqual(0, get_wa_fire_data.get_containment(f))
        f = {}
        self.assertEqual(0, get_wa_fire_data.get_containment(f))
        f = {"Percent Contained":"40%"}
        self.assertEqual(40, get_wa_fire_data.get_containment(f))
        f = {"Percent Contained":"40 %"}
        self.assertEqual(40, get_wa_fire_data.get_containment(f))
        f = {"Percent Contained":"     "}
        self.assertEqual(0, get_wa_fire_data.get_containment(f))

    def test_get_value(self):
        fn = lambda x: x.split()[0]
        k = "Acres"
        f = None
        self.assertEqual(0, utilities.get_value(f, k, ",", fn))
        f = {}
        self.assertEqual(0, utilities.get_value(f, k, ",", fn))
        f = {"Acres":"40 Acres"}
        self.assertEqual(40, utilities.get_value(f, k, ",", fn))
        f = {"Acres":" ,"}
        self.assertEqual(0, utilities.get_value(f, k, ",", fn))
        f = {"Acres":"     "}
        self.assertEqual(0, utilities.get_value(f, k, ",", fn))

        f = {"Acres":"  10 "}
        fn = lambda x: " "  # Contorted edge case to make sure we get code coverage on a test.
        self.assertEqual(0, utilities.get_value(f, k, ",", fn))

    def test_summarize(self):
        data_store = DataStore("data/data_wa")
        # Just running it forces all data to be loaded and checked that it's valid.
        summary = get_wa_fire_data.summarize(data_store)
        print(summary)

    def test_summary_no_yesterday(self):
        # Check the 'only have one day of data' case. (no yesterday)
        data_store = DataStore("data/data_test/data_wa")
        # Just running it forces all data to be loaded and checked that it's valid.
        summary = get_wa_fire_data.summarize(data_store)
        print(summary)


    def test_get_unique_id(self):
        incident = {
            'Incident Number': 1,
            'Incident Name': "Name!"
        }
        self.assertEqual(1, get_wa_fire_data.get_unique_id(incident))
        incident = {
            'Incident Name': "Name!"
        }
        self.assertEqual("Name!", get_wa_fire_data.get_unique_id(incident))
        incident = {}
        with self.assertRaises(KeyError):
            get_wa_fire_data.get_unique_id(incident)

    def test_parse(self):
        data = get_wa_fire_data.get_data_store().get_source_data(date(2021,6,27))
        results = get_wa_fire_data.parse(data)
        self.assertEqual(3, len(results))
        self.assertEqual("6,679", results[0]["Acres"])

    def test_get_annual_acres(self):
        data_store = DataStore("data/data_test/data_wa")
        # Should be no data in 2019, test for that.
        days, totals = get_wa_fire_data.get_annual_acres(data_store, 2019)
        self.assertEqual(0, len(days))

        days, total = get_wa_fire_data.get_annual_acres(data_store, 2020)
        self.assertEqual(1, len(days))
        self.assertEqual(2020, days[0][0])
        self.assertEqual(9, days[0][1])
        self.assertEqual(12, days[0][2])
        self.assertEqual(1530890, total)

