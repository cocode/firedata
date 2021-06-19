from unittest import TestCase
from get_cal_fire_data import get_delta
import json


class Test(TestCase):
    def test_get_delta(self):
        with open("data/data_test/firedata_2020_09_09.json") as f:
            f1 = json.load(f)
        with open("data/data_test/firedata_2020_09_09.json") as f:
            f2 = json.load(f)
        a, b = get_delta(f1, f2, "not_in_f1_or_f2", 3)
        self.assertEqual(a, "   ")
        self.assertEqual(b,  0)

        a, b = get_delta(f1, f2, "unchanged", 3)
        self.assertEqual(a, "   ") # Not sure blank for no change is best.
        self.assertEqual(b,  0)
