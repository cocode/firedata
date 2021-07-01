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


