from unittest import TestCase

import get_historical_data


class Test(TestCase):
    def test_get_fed_history(self):
        history = get_historical_data.get_fed_history()

        for year, h in zip(range(1983, 2021), history):
            self.assertEqual(year, int(h[0]))
            for one in h:
                self.assertTrue(int(one) > 0)
