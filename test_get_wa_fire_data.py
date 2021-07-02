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

