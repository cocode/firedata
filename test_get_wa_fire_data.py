from unittest import TestCase

import get_wa_fire_data
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
        self.assertEqual(0, get_wa_fire_data.get_value(f, k, ",", fn))
        f = {}
        self.assertEqual(0, get_wa_fire_data.get_value(f, k, ",", fn))
        f = {"Acres":"40 Acres"}
        self.assertEqual(40, get_wa_fire_data.get_value(f, k, ",", fn))
        f = {"Acres":" ,"}
        self.assertEqual(0, get_wa_fire_data.get_value(f, k, ",", fn))
        f = {"Acres":"     "}
        self.assertEqual(0, get_wa_fire_data.get_value(f, k, ",", fn))


