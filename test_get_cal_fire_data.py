from unittest import TestCase
from get_cal_fire_data import get_delta
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
