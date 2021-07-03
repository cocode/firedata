from datetime import date
from unittest import TestCase

import get_az_fire_data


class Test(TestCase):
    def test_parse(self):
        data_store = get_az_fire_data.get_data_store()
        data = data_store.get_source_data(date(2021, 6, 25))
        results = get_az_fire_data.parse(data)
        self.assertEqual(921, results["number_of_fires"])
        self.assertEqual(468289, results["acres_burned"])

