from unittest import TestCase
from get_us_fire_data import get_size


class Test(TestCase):
    def test_get_size(self):
        f = None
        self.assertIsNone(get_size(f))
        f = {}
        with self.assertRaises(KeyError):
            self.assertIsNone(get_size(f))
        f = {"Size":"40 Acres"}
        self.assertEqual(40, get_size(f))

