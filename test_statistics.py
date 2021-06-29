from unittest import TestCase

from statistics import Statistics


class TestStatistics(TestCase):
    def test_verify_ids_unique(self):
        s = Statistics()
        data = [
            {
                "a":1,
                "id":12
            },
            {
                "b":1,
                "id":12
            }
        ]
        get_unique_id = lambda x: x["id"]
        with self.assertRaises(Exception):
            s.verify_ids_unique(data, get_unique_id)
        data[0]['id'] = 99
        # Should not raise now.
        s.verify_ids_unique(data, get_unique_id)
