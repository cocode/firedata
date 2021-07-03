from unittest import TestCase

import get_historical_data


class Test(TestCase):
    def test_get_fed_history(self):
        history = get_historical_data.get_fed_history()

        for year, h in zip(range(1983, 2021), history):
            self.assertEqual(year, int(h[0]))
            for one in h:
                self.assertTrue(int(one) > 0)

    def test_get_2019_data(self):
        data = get_historical_data.get_2019_data()
        self.assertEqual(int(data[7]), int(data[1]) + int(data[3]) + int(data[5]))
        self.assertEqual(int(data[8]), int(data[2]) + int(data[4]) + int(data[6]))

    def test_get_2020_data(self):
        data = get_historical_data.get_2020_data()
        self.assertEqual(int(data[7]), int(data[1]) + int(data[3]) + int(data[5]))
        self.assertEqual(int(data[8]), int(data[2]) + int(data[4]) + int(data[6]))

